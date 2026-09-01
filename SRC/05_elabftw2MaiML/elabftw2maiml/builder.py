"""
ExperimentData (eLabFTWから取得したデータ) -> MaiML <maiml> ルート要素、への変換本体。

マッピング方針 (READMEにも記載):

  document/creator   = 実験のカスタムフィールド (既定候補: 「使用装置」等) から取得。
                        フィールドが無ければこのコンバータ自身にフォールバックする。
  document/vendor    = 同様にカスタムフィールド (既定候補: 「装置メーカー」等) から取得。
                        creator/vendorとも見つからなければ Deltablot にフォールバックする。
  document/owner     = eLabFTW実験のオーナー (ユーザー)。ユーザーIDから名前ベースUUIDを生成、
                        同一ユーザーは常に同一UUIDになる。
  document/instrument = カスタムフィールドからcreatorを特定できた場合のみ、同じ表示名で追加する。
  document/date       = 実験の date (作成日)。

  protocol/method     = 実験1件 = 1 method。
  protocol/.../pnml    = 「このSTEPが直接導入した材料/条件のplace」-> 各StepのTransition
                          -> 「このSTEPの出力place」という直列ペトリネット。
                          STEP本文の "#123" 記法でSTEPに割り当てられたリンクアイテムがあれば、
                          そのSTEP専用のplace/materialTemplate/conditionTemplateを作る。
                          どのSTEPにも割り当てられなかったリンクアイテムは、従来通り
                          最初のSTEPの共通材料/条件として扱う (後方互換)。
  protocol/.../program/instruction
                       = eLabFTWの各Step (Steps API) = 1 instruction。

  materialTemplate     = STEPごとに、そのSTEPが直接導入した生のリンクアイテム分をまず作る
                          (placeRefのみ、templateRefなし)。
                          さらに最終STEP以外の各STEPについて、「このSTEPの処理結果としての
                          中間材料」を表す派生materialTemplateを1つ追加する。この派生
                          templateは、(a)そのSTEP自身が生の材料を導入していればその最初の
                          materialTemplateへ、(b)導入していなければ前STEPまでの派生材料
                          templateへ、templateRefで接続する (materialTemplate->materialTemplate
                          なのでMaiML仕様 REF-02上正当)。これにより
                          material-1 -> [STEP1] -> material-2 -> [STEP2] -> material-3 -> ...
                          という材料の系譜をprotocol層で正しく表現する。

  conditionTemplate    = STEPごとに、そのSTEPが直接導入した条件 (カスタムフィールド等) が
                          あれば1つ作る (無ければそのSTEPには作らない)。系譜的な連結は不要
                          (各STEPの条件は独立した計測値とみなす)。

  resultTemplate        = そのSTEP固有の結果データ (#123タグ付けされたresult役割アイテム、
                          または最終STEPの本文/タグ/添付ファイル) がある場合のみ作る。
                          直前に作られたresultTemplateがあればtemplateRefで接続し
                          (resultTemplate->resultTemplateなのでREF-02上正当)、無ければ
                          templateRef自体を省略する (XSD上minOccurs=0)。

  data/results/material/condition/result
                       = 上記テンプレートに対応する実測値インスタンス。resultTemplateを
                         持つSTEPの result インスタンスは、同じ接続パターンを instanceRef
                         (templateRefのインスタンス層版) で反映する。

  eventLog             = 各StepについてSTART/COMPLETEイベントを記録。
                          resultTemplateを持つ (=結果を記録した) 各Stepのcompleteイベントに
                          resultsRef を付与し、R-16 (lifecycle:transition=complete 必須) を
                          満たす。
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from lxml import etree

from . import maiml_xml as mx
from .model import ExperimentData, Party, PropertyValue, LinkedItem, Step
from .uuids import new_uuid, named_uuid

VENDOR_KEY = ("elabftw-vendor", "deltablot")
CREATOR_SOFTWARE_VERSION = "1.0.0"  # このコンバータ自体のバージョン。上げたらUUIDが変わる。


def _dt(value: Optional[datetime]) -> str:
    """xs:dateTime (ISO8601) 文字列に変換。tz naiveならUTC付与。"""
    if value is None:
        value = datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _property_from_pv(pv: PropertyValue) -> etree._Element:
    return mx.property_el(
        key=pv.key,
        xsi_type=pv.xsi_type,
        value=pv.value,
        values=pv.values,
        description=pv.description,
        format_string=pv.format_string,
        units=pv.units,
        scale_factor=pv.scale_factor,
    )


class MaimlBuilder:
    def __init__(self, ns_prefix: str = "ns1", ns_uri: str = "https://example.org/maiml/mylab",
                 elab_host: str = "elabftw.local"):
        self.ns_prefix = ns_prefix
        self.ns_uri = ns_uri
        self.elab_host = elab_host

    # -- creator/vendor/owner のParty定義 -------------------------------

    def _software_creator(self) -> Party:
        return Party(
            key=f"elabftw-to-maiml/{CREATOR_SOFTWARE_VERSION}",
            name=f"{self.ns_prefix}:elabftw-to-maiml",
            description="eLabFTW REST API v2 (elabapi-python) 経由で取得した実験データをMaiMLに変換するツール",
        )

    def _vendor(self) -> Party:
        return Party(key="|".join(VENDOR_KEY), name=f"{self.ns_prefix}:Deltablot",
                     description="eLabFTW開発元")

    # -- document ---------------------------------------------------------

    def _build_document(self, exp: ExperimentData) -> etree._Element:
        creator_party = exp.creator or self._software_creator()
        vendor_party = exp.vendor or self._vendor()

        creator_uuid = named_uuid(creator_party.key)
        vendor_uuid = named_uuid(vendor_party.key)

        vendor_el = mx.E(
            "vendor",
            *mx.global_content(vendor_uuid, description=vendor_party.name),
            id="vendor_of_creator",
        )

        instrument_els = []
        instrument_ref_els = []
        for idx, instrument_party in enumerate(exp.instruments):
            instrument_uuid = named_uuid(instrument_party.key)
            instrument_id = f"instrument_{idx + 1}"
            instrument_els.append(mx.E(
                "instrument",
                *mx.global_content(instrument_uuid, description=instrument_party.name),
                id=instrument_id,
            ))
            instrument_ref_els.append(mx.ref_el("instrumentRef", instrument_id, f"iref_creator_{idx + 1}"))

        creator_children = [mx.ref_el("vendorRef", "vendor_of_creator", "vref_creator")]
        creator_children.extend(instrument_ref_els)

        creator_el = mx.E(
            "creator",
            *mx.global_content(creator_uuid, description=creator_party.name),
            *creator_children,
            id="creator_instrument",
        )

        owner_party = exp.owner or Party(key=f"elabftw-unknown-owner@{self.elab_host}", name="unknown")
        owner_uuid = named_uuid(owner_party.key)
        owner_el = mx.E(
            "owner",
            *mx.global_content(owner_uuid, description=owner_party.name),
            id="owner_experiment",
        )

        doc_uuid = new_uuid()
        doc_children = mx.global_content(doc_uuid, description=exp.title)
        document_children = [creator_el, vendor_el, owner_el, *instrument_els]
        return mx.E(
            "document",
            *doc_children,
            *document_children,
            mx.text_el("date", _dt(exp.date)),
            id=f"document_exp{exp.elab_id}",
        )

    # -- protocol -----------------------------------------------------------

    def _build_protocol(self, exp: ExperimentData):
        """
        戻り値: (protocol要素, method_id, program_id,
                 {step_key: instruction_id},
                 {step_key: [(LinkedItem, materialTemplate_id), ...]},   # このSTEPが直接導入した生の材料
                 {step_key: (conditionTemplate_id, [PropertyValue,...])},  # このSTEPの条件 (あるSTEPのみ)
                 [(step_key, resultTemplate_id, is_last, [PropertyValue,...]), ...])  # resultTemplateを持つSTEPのみ、STEP順
        """
        method_id = f"method_exp{exp.elab_id}"
        pnml_id = f"pnml_exp{exp.elab_id}"
        program_id = f"prog_exp{exp.elab_id}"
        p_result_out = "p_result_out"

        steps = exp.steps or [Step(elab_id=0, title="measurement")]
        n_steps = len(steps)

        # PLACE -> STEP(transition) -> PLACE -> STEP(transition) -> ... -> PLACE
        # (MaiMLのペトリネットはtransition同士を直接つなげず、必ず間にplaceを挟む)
        places = []
        transitions = []
        arcs = []
        instructions = []
        material_templates = []
        condition_templates = []
        result_templates = []

        step_instruction_ids: dict = {}
        step_material_infos: dict = {}    # step_key -> [(item, tmpl_id), ...] (このSTEPが直接導入した生材料)
        step_condition_infos: dict = {}   # step_key -> (cond_tmpl_id, [PropertyValue,...])
        step_result_template_ids: list = []  # [(step_key, tmpl_id, is_last, [PropertyValue,...]), ...]

        arc_n = 0
        prev_output_place = None   # 直前のSTEPの出力place (次のSTEPの入力として常に引き継ぐ)
        material_chain_id = None   # 直近の「材料の系譜」テンプレートid (生材料の先頭 or 前STEPの派生出力)
        result_chain_id = None     # 直近のresultTemplate id (resultTemplateを持つ最新のSTEP)

        for i, step in enumerate(steps):
            step_key = step.elab_id if step.elab_id else i
            is_last = (i == n_steps - 1)
            t_id = f"t_step_{step_key}"
            transitions.append(mx.E("transition", id=t_id))

            # -- このSTEPが直接導入する材料/条件 (#xxタグ付け分。STEP0のみ未割当プールも合流) ---
            own_materials = list(step.materials)
            own_conditions = list(step.condition_properties)
            if i == 0:
                own_materials = list(exp.materials) + own_materials
                own_conditions = list(exp.condition_properties) + own_conditions
                if not own_materials:
                    own_materials = [LinkedItem(elab_id=0, title="(no linked item)")]

            # -- material: 導入がある場合のみこのSTEP専用のplaceを作る -----------------------
            step_material_infos[step_key] = []
            fresh_material_place = None
            first_new_material_tmpl_id = None
            if own_materials:
                fresh_material_place = f"p_material_{step_key}"
                places.append(mx.E("place", id=fresh_material_place))
                for item in own_materials:
                    tmpl_id = f"mattmpl_{step_key}_{item.elab_id}"
                    props = [_property_from_pv(p) for p in item.properties]
                    material_templates.append(mx.E(
                        "materialTemplate",
                        *mx.global_content(new_uuid(), description=item.title, properties=props),
                        mx.ref_el("placeRef", fresh_material_place, f"pref_mat_{step_key}_{item.elab_id}"),
                        id=tmpl_id,
                    ))
                    step_material_infos[step_key].append((item, tmpl_id))
                    if first_new_material_tmpl_id is None:
                        first_new_material_tmpl_id = tmpl_id

            # -- condition: 導入がある場合のみこのSTEP専用のplace/templateを作る -------------
            fresh_condition_place = None
            if own_conditions:
                fresh_condition_place = f"p_condition_{step_key}"
                places.append(mx.E("place", id=fresh_condition_place))
                cond_tmpl_id = f"condtmpl_step_{step_key}"
                cond_props_els = [_property_from_pv(p) for p in own_conditions]
                condition_templates.append(mx.E(
                    "conditionTemplate",
                    *mx.global_content(new_uuid(), properties=cond_props_els),
                    mx.ref_el("placeRef", fresh_condition_place, f"pref_cond_{step_key}"),
                    id=cond_tmpl_id,
                ))
                step_condition_infos[step_key] = (cond_tmpl_id, own_conditions)

            # -- transitionへの入力arc --------------------------------------------------
            if i == 0:
                if fresh_material_place:
                    arc_n += 1
                    arcs.append(mx.E("arc", id=f"a{arc_n}", source=fresh_material_place, target=t_id))
            else:
                arc_n += 1
                arcs.append(mx.E("arc", id=f"a{arc_n}", source=prev_output_place, target=t_id))
                if fresh_material_place:
                    arc_n += 1
                    arcs.append(mx.E("arc", id=f"a{arc_n}", source=fresh_material_place, target=t_id))
            if fresh_condition_place:
                arc_n += 1
                arcs.append(mx.E("arc", id=f"a{arc_n}", source=fresh_condition_place, target=t_id))

            # -- transitionからの出力arc ---------------------------------------------------
            out_place = p_result_out if is_last else f"p_mid_{step_key}"
            if not is_last:
                places.append(mx.E("place", id=out_place))
            arc_n += 1
            arcs.append(mx.E("arc", id=f"a{arc_n}", source=t_id, target=out_place))
            prev_output_place = out_place

            # -- instruction ---------------------------------------------------------------
            instr_id = f"instr_step_{step_key}"
            step_instruction_ids[step_key] = instr_id
            instructions.append(mx.E(
                "instruction",
                *mx.global_content(new_uuid(), description=step.title),
                mx.ref_el("transitionRef", t_id, f"tref_{t_id}"),
                id=instr_id,
            ))

            # -- 材料の系譜: このSTEPの処理結果としての中間材料 (最終STEP以外) -----------------
            chain_source_id = first_new_material_tmpl_id if first_new_material_tmpl_id is not None else material_chain_id
            if not is_last:
                derived_id = f"mattmpl_out_step_{step_key}"
                derived_children = list(mx.global_content(new_uuid()))
                derived_children.append(mx.ref_el("placeRef", out_place, f"pref_matout_{step_key}"))
                if chain_source_id is not None:
                    derived_children.append(mx.ref_el("templateRef", chain_source_id, f"tref_matout_{step_key}"))
                material_templates.append(mx.E("materialTemplate", *derived_children, id=derived_id))
                material_chain_id = derived_id
            else:
                material_chain_id = chain_source_id

            # -- resultTemplate: このSTEP固有の結果データがある場合、または最終STEPの場合のみ ---
            own_result_props = list(step.result_properties)
            if is_last:
                own_result_props = own_result_props + list(exp.result_properties)

            if own_result_props or is_last:
                restmpl_id = f"restmpl_step_{step_key}"
                props_els = [_property_from_pv(p) for p in own_result_props]
                content_children = list(mx.global_content(new_uuid(), properties=props_els))
                content_children.append(mx.ref_el("placeRef", out_place, f"pref_res_{step_key}"))
                if result_chain_id is not None:
                    content_children.append(mx.ref_el("templateRef", result_chain_id, f"tref_{restmpl_id}"))
                result_templates.append(mx.E("resultTemplate", *content_children, id=restmpl_id))
                step_result_template_ids.append((step_key, restmpl_id, is_last, own_result_props))
                result_chain_id = restmpl_id

        places.append(mx.E("place", id=p_result_out))

        pnml_el = mx.E(
            "pnml",
            *mx.global_content(new_uuid()),
            *places,
            *transitions,
            *arcs,
            id=pnml_id,
        )

        program_el = mx.E(
            "program",
            *mx.global_content(new_uuid()),
            *instructions,
            *material_templates,
            *condition_templates,
            *result_templates,
            id=program_id,
        )

        method_el = mx.E(
            "method",
            *mx.global_content(new_uuid(), description=exp.title),
            pnml_el,
            program_el,
            id=method_id,
        )

        protocol_el = mx.E(
            "protocol",
            *mx.global_content(new_uuid()),
            method_el,
            id=f"protocol_exp{exp.elab_id}",
        )

        return (protocol_el, method_id, program_id, step_instruction_ids,
                step_material_infos, step_condition_infos, step_result_template_ids)

    # -- data ---------------------------------------------------------------

    def _build_data(self, exp: ExperimentData, step_material_infos: dict,
                     step_condition_infos: dict, step_result_template_ids: list):
        """戻り値: (data要素, results_id, resultTemplateを持つstep_keyのリスト)"""
        results_id = f"results_exp{exp.elab_id}"

        material_instances = []
        for step_key, items in step_material_infos.items():
            for item, tmpl_id in items:
                props = [_property_from_pv(p) for p in item.properties]
                inst_id = f"material_{step_key}_{item.elab_id}"
                material_instances.append(mx.E(
                    "material",
                    *mx.global_content(new_uuid(), description=item.title, properties=props),
                    id=inst_id,
                    ref=tmpl_id,
                ))

        condition_instances = []
        for step_key, (cond_tmpl_id, cond_props) in step_condition_infos.items():
            cond_props_els = [_property_from_pv(p) for p in cond_props]
            condition_instances.append(mx.E(
                "condition",
                *mx.global_content(new_uuid(), properties=cond_props_els),
                id=f"condition_step_{step_key}",
                ref=cond_tmpl_id,
            ))

        # result: resultTemplateを持つSTEPごとに1つ、instanceRefで同じ系譜を反映する。
        #   instanceRefは「同種の要素(result)」を参照する必要がある (MaiML仕様 REF-02)。
        #   系譜上、直前に作られたresult(resultTemplateを持つSTEP)が無ければinstanceRef自体を
        #   省略する (XSD上minOccurs=0)。
        result_instances = []
        prev_result_instance_id = None
        steps_with_result = []
        for (step_key, tmpl_id, is_last, props_list) in step_result_template_ids:
            inst_id = f"result_step_{step_key}"
            steps_with_result.append(step_key)

            if prev_result_instance_id is None:
                instance_ref_el = None
            else:
                instance_ref_el = mx.ref_el("instanceRef", prev_result_instance_id, f"iref_{inst_id}")

            if is_last:
                insertions = [
                    mx.insertion_el(uri=u.uri, file_hash_b64=u.hash_b64, hash_method=u.hash_method, fmt=None)
                    for u in exp.uploads
                ]
            else:
                insertions = None

            props_els = [_property_from_pv(p) for p in props_list]
            content_children = list(mx.global_content(new_uuid(), insertions=insertions, properties=props_els))
            if instance_ref_el is not None:
                content_children.append(instance_ref_el)

            result_instances.append(mx.E("result", *content_children, id=inst_id, ref=tmpl_id))
            prev_result_instance_id = inst_id

        results_el = mx.E(
            "results",
            *mx.global_content(new_uuid()),
            *material_instances,
            *condition_instances,
            *result_instances,
            id=results_id,
        )

        data_el = mx.E(
            "data",
            *mx.global_content(new_uuid()),
            results_el,
            id=f"data_exp{exp.elab_id}",
        )
        return data_el, results_id, steps_with_result

    # -- eventLog -------------------------------------------------------------

    def _build_event_log(self, exp: ExperimentData, method_id: str, program_id: str,
                          step_instruction_ids: dict, results_id: str, steps_with_result: list):
        steps = exp.steps or [Step(elab_id=0, title="measurement", finished_at=exp.date, is_finished=True)]
        steps_with_result_set = set(steps_with_result)

        events = []
        for i, step in enumerate(steps):
            key = step.elab_id if step.elab_id else i
            instr_id = step_instruction_ids[key]
            instance_uuid = new_uuid()

            start_ts = _dt(step.started_at or exp.date)
            events.append(mx.E(
                "event",
                *mx.global_content(new_uuid(), properties=[
                    mx.property_el("concept:instance", "uuidType", value=instance_uuid),
                    mx.property_el("lifecycle:transition", "stringType", value="start"),
                    mx.property_el("time:timestamp", "dateTimeType", value=start_ts),
                ]),
                id=f"event_start_{key}",
                ref=instr_id,
            ))

            complete_ts = _dt(step.finished_at or exp.date)
            complete_children = mx.global_content(new_uuid(), properties=[
                mx.property_el("concept:instance", "uuidType", value=instance_uuid),
                mx.property_el("lifecycle:transition", "stringType", value="complete"),
                mx.property_el("time:timestamp", "dateTimeType", value=complete_ts),
            ])
            complete_event = mx.E("event", *complete_children, id=f"event_complete_{key}", ref=instr_id)
            if key in steps_with_result_set:
                # R-16: 結果を記録したSTEPのcompleteイベントに resultsRef を付与する。
                complete_event.append(mx.ref_el("resultsRef", results_id, f"resref_{key}"))
            events.append(complete_event)

        trace_id = f"trace_exp{exp.elab_id}"
        trace_el = mx.E(
            "trace",
            *mx.global_content(new_uuid()),
            *events,
            id=trace_id,
            ref=program_id,
        )

        log_id = f"log_exp{exp.elab_id}"
        log_el = mx.E(
            "log",
            *mx.global_content(new_uuid()),
            trace_el,
            id=log_id,
            ref=method_id,
        )

        event_log_el = mx.E(
            "eventLog",
            *mx.global_content(new_uuid()),
            log_el,
            id=f"eventLog_exp{exp.elab_id}",
        )
        return event_log_el

    # -- root -------------------------------------------------------------

    def build(self, exp: ExperimentData) -> etree._Element:
        nsmap = {
            None: mx.NS_MAIML,
            "xsi": mx.NS_XSI,
            "ds": mx.NS_DS,
            self.ns_prefix: self.ns_uri,
            "concept": "http://www.xes-standard.org/concept.xesext#",
            "lifecycle": "http://www.xes-standard.org/lifecycle.xesext#",
            "time": "http://www.xes-standard.org/time.xesext#",
        }
        root = etree.Element(f"{{{mx.NS_MAIML}}}maiml", nsmap=nsmap)
        root.set("version", "1.0")
        root.set("features", "nested-attributes")
        root.set(f"{{{mx.NS_XSI}}}type", "maimlRootType")

        document_el = self._build_document(exp)
        (protocol_el, method_id, program_id, step_instruction_ids,
         step_material_infos, step_condition_infos, step_result_template_ids) = self._build_protocol(exp)
        data_el, results_id, steps_with_result = self._build_data(
            exp, step_material_infos, step_condition_infos, step_result_template_ids)
        event_log_el = self._build_event_log(
            exp, method_id, program_id, step_instruction_ids, results_id, steps_with_result)

        root.append(document_el)
        root.append(protocol_el)
        root.append(data_el)
        root.append(event_log_el)
        return root

    def to_bytes(self, exp: ExperimentData) -> bytes:
        root = self.build(exp)
        return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
