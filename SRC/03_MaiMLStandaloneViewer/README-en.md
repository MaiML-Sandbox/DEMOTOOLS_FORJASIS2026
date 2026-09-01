# MaiMLStandaloneViewer

A standalone web application for visualizing and analyzing MaiML (Measurement Analysis Instrument Markup Language) files.

## 🌟 Key Features

### 📊 Graph Visualization
- **Petri net–based workflow visualization**: displays the state transitions of an experimental process as a node graph
  - **Place (circle)**: represents the state of a sample or data
  - **Transition (rectangle)**: represents a process or event
- **Reference relationship visualization** (each type can be toggled on/off in the 🔗 Link Visibility toolbox):
  - **Template Ref (yellow dashed line)**: reference relationships between templates
  - **Instance Ref (green dashed line)**: reference relationships between instances
  - **Chain Link (orange dashed line)**: chain (`<chain>`) relationships between different MaiML files, including hash-based integrity verification
  - **Parent Link (purple dashed line)**: visualization of chain (`<parent>`) relationships with the revision source file
  - **Same UUID: Template (blue-violet dashed line)**: correspondence between Template nodes that share the same UUID
  - **Same UUID: Instance (light purple dashed line)**: correspondence between Instance nodes that share the same UUID

### 📄 Metadata Management and Display
- **Document Info panel**: unified display of author, UUID, description, and vendor information
- **Detail panel**: displays related template/instance information for the selected node
- **Template/instance hierarchy view**: automatically extracts the relevant data when a node is selected

### 📁 File Support
- **`.maiml` file support**: full support for the MaiML standard format
- **`.zip` archive support**: automatically links MaiML files inside a ZIP with their associated images/data
- **Embedded file preview**:
  - Direct display of images (JPG, PNG, TIFF, etc.)
  - Table display of CSV/text data
  - Multi-page TIFF support

### 🎨 UI/UX Features
- **Light/dark theme support**: seamless switching via CSS variables
- **Responsive design**: horizontal/vertical resizers to adjust panel sizes
- **Graph operations**:
  - Zoom with the mouse wheel (0.25× to 6×)
  - Pan by dragging
  - Manual node placement (Drag Edit checkbox)

### 🎯 Layout Features
- **Force-directed layout**: automatic placement based on a physics model
- **Dagre hierarchical layout**: automatic hierarchical arrangement
- **Grid display/snap**: alignment and placement assistance

### 🤖 AI Analysis Features
- **Cloud / local LLM switching**: AI summarization of detailed data
  - **☁️ Cloud (Gemini)**: integrates with the Google Gemini API; high accuracy and speed, but data is sent to Google's servers
  - **🖥️ Local (Ollama)**: uses a local LLM (Ollama) to summarize without sending data externally (requires Ollama to be installed)
- **Multiple prompt templates**:
  - Quick Summary
  - Standard Summary
  - Detailed Report
  - Custom Prompt (user-defined)
- **Results shown in Markdown format**, with save/copy functionality

### 📊 Data Plotting Features
- **Three chart types**:
  - **Line**: shows time-series trends
  - **Bar**: shows a histogram
  - **Scatter**: shows correlation analysis
- **Interactive controls**: zoom, pan, and reset
- Integrated with Chart.js + a chart zoom plugin

### 📈 Metadata Export
Supports exporting data in multiple formats:
- **Excel (.xlsx)**: listed by sheet structure
- **JSON (.json)**: raw data preserving the hierarchical structure
- **CSV (.csv)**: for use with general-purpose tools

### 🔐 XML Encrypted Data Support (JIS K0200 compliant)
- **AES-256-GCM + PBKDF2-SHA256 decryption support**: compliant with W3C XML Encryption 1.1
- **Encryption banner notification**: shown automatically when encrypted data is detected
- **Batch decryption**: decrypt all elements at once with the "Decrypt All" button
- **Individual decryption option**: decrypt node by node, step by step
- **Password caching**: automatically reused during the session
- ⚠️ **Limitation**: only the password-based method is supported (RSA/key-wrap methods are not supported)

### 🛢️ Data Lake (bulk management of a local folder)
- **Folder connection**: connect an entire local folder; recursively scans and lists `.maiml` / `.maiml.zip` files, including those in subfolders
- **Search/filter**: narrow down files by keyword (file name, sample name, operator name, etc.), measurement date/time range, or instrument name
- **Sorting**: sort by date (newest/oldest first), file name, or file size
- **Bulk loading**: select filtered files and load multiple files into the viewer at once
- **Cross-session cache**: caches the folder index in `localStorage` for instant restoration on next launch; use "Sync / Re-Verify" to rescan and reconnect
- ℹ️ **Supported browsers**: Chrome / Edge (uses the File System Access API). Firefox / Safari fall back to limited functionality
- Folder access is read-only (no files are modified or deleted)

### 🔏 XML Signature Verification (ds:Signature)
- **Automatic signature integrity verification**: when loading a MaiML file signed per the W3C XML Signature standard (ECDSA P-256), the viewer automatically verifies that the file has not been altered since it was signed
- **Verification result badge**: shown in the Document Metadata panel in the upper right
  - ✅ **Integrity OK** — the signature and hash match the file contents
  - ❌ **Integrity check failed** — a mismatch was detected in the hash or signature value
  - ⚠️ **Unsupported** — an unsupported algorithm other than ECDSA P-256 (e.g., RSA)
- ⚠️ **Note**: this verification only checks integrity ("has it been altered since signing?") — it does not prove the signer's authenticity ("who signed it"), since the public key is bundled within the file itself

## 🚀 How to Use

### Installation and Launch
1. Download `HTML-MaiMLViewer.html`
2. Open it directly in your browser (no server required)
3. Or serve it from any web server

### Basic Operations

#### Loading Files
Load files using the **📂Upload Files…** button in the top-left of the screen, or by dragging and dropping onto the screen.

- **Supported formats**: `.maiml` files and `.zip` files containing them
- **ZIP support**: when you upload a ZIP file, the MaiML files inside are automatically linked with their image/data files and expanded
- If you want to manage a local folder in bulk, the **🛢️ Data Lake** feature is also available (Chrome/Edge only; see "Data Lake" above for details)

#### Graph Operations

| Operation | Method |
|------|------|
| Pan | Drag on an empty area |
| Zoom | Mouse wheel |
| Move a node | Drag each node (circle or rectangle) (enable/disable with the **Drag Edit** checkbox) |
| Auto-adjust layout | **Auto Layout** (force-directed model) or **Dagre Layout** (hierarchical) button |
| Reset placement | **Reset Position** button |
| Grid display/snap | **Show Grid** / **Snap to Grid** checkboxes |
| Toggle light/dark | **🌙 Theme** button in the header |
