# Design Document: RRC Parsing Accuracy Enhancement

## 1. Overview

This design document specifies the architecture and implementation approach for enhancing the QMDL Call Flow Analyzer's RRC and NAS message parsing capabilities. The system currently processes QMDL/HDF/PCAP files containing LTE/NR protocol messages, but requires improvements to handle all message types, encapsulation formats, and edge cases accurately.

### 1.1 Goals

- Parse 100% of LTE RRC, NR RRC, NAS EPS, and NAS 5GS message types
- Handle GSMTAPv3 encapsulated messages correctly
- Support multiple tshark JSON output formats (hyphen and underscore variants)
- Extract nested messages (NAS within RRC, NR RRC within LTE RRC)
- Correctly identify message direction (UL/DL) and network nodes
- Maintain backward compatibility with existing functionality

### 1.2 Non-Goals

- Real-time packet capture (system processes pre-captured files only)
- Protocol validation or conformance testing
- Message modification or injection capabilities

## 2. Architecture

### 2.1 System Components

```
┌─────────────┐
│   Web UI    │ (templates/index.html)
└──────┬──────┘
       │ HTTP POST /upload
       ▼
┌─────────────────────────────────────────┐
│         Flask Application (app.py)       │
│  ┌────────────────────────────────────┐ │
│  │  File Upload Handler               │ │
│  └────────┬───────────────────────────┘ │
│           ▼                              │
│  ┌────────────────────────────────────┐ │
│  │  Conversion Pipeline               │ │
│  │  • convert_to_pcap()               │ │
│  │  • convert_pcap_to_json()          │ │
│  └────────┬───────────────────────────┘ │
│           ▼                              │
│  ┌────────────────────────────────────┐ │
│  │  Parsing Engine                    │ │
│  │  • parse_call_flow()               │ │
│  │  • extract_message_info()          │ │
│  │  • determine_direction_and_nodes() │ │
│  └────────┬───────────────────────────┘ │
└───────────┼──────────────────────────────┘
            ▼
     ┌──────────────┐
     │  JSON Output │
     └──────────────┘
```

### 2.2 Data Flow

1. **Upload**: User uploads QMDL/HDF/PCAP file
2. **PCAP Conversion**: scat converts QMDL/HDF → PCAP (skipped for PCAP input)
3. **JSON Conversion**: tshark converts PCAP → JSON with full protocol details
4. **Parsing**: Python parser extracts message information from JSON
5. **Visualization**: Web UI renders call flow diagram

## 3. Detailed Design

### 3.1 Message Extraction Strategy

The parser uses a multi-layered approach to handle various JSON structures:


#### 3.1.1 Layer Key Normalization

**Design Decision**: Support both hyphen and underscore variants of protocol layer keys.

**Rationale**: Different tshark versions and configurations output different key formats ('lte-rrc' vs 'lte_rrc'). Supporting both ensures compatibility across environments.

**Implementation**:
```python
# Check for both variants
nr_rrc_key = 'nr-rrc' if 'nr-rrc' in layers else 'nr_rrc' if 'nr_rrc' in layers else None
lte_rrc_key = 'lte-rrc' if 'lte-rrc' in layers else 'lte_rrc' if 'lte_rrc' in layers else None
```

#### 3.1.2 Message Extraction Hierarchy

**Design Decision**: Use a cascading search strategy with three methods.

**Rationale**: Messages can appear in different JSON structures depending on encapsulation and tshark version. A hierarchical approach ensures all cases are covered.

**Method 1: Standard RRC Message Structure**
- Look for `*_Message_element` keys (e.g., `UL_DCCH_Message_element`)
- Navigate through `message_tree` → `c1_tree` → actual message
- Used for: Standard LTE/NR RRC messages

**Method 2: GSMTAPv3 Direct Messages**
- Look for message elements directly in protocol layer (e.g., `nr-rrc.RRCReconfiguration_element`)
- Skip Message_element wrapper
- Used for: GSMTAPv3 encapsulated messages

**Method 3: Top-Level Direct Messages**
- Look for message elements at layers root level
- Used for: Alternative encapsulation formats

### 3.2 Protocol-Specific Parsing

#### 3.2.1 NR RRC Messages

**Key Patterns**:
- Message wrapper: `nr-rrc.{CHANNEL}_Message_element` (e.g., `DL_DCCH_Message_element`)
- Message tree: `nr-rrc.{channel}_Message.message_tree`
- Choice tree: `nr-rrc.c1_tree`
- Actual message: `nr-rrc.{MessageName}_element`

**Special Cases**:
- **MIB**: Found directly in `BCCH_BCH_Message` as `nr-rrc.mib_element`
- **SystemInformationBlockType1**: Found in `c1_tree` as `systemInformationBlockType1`

**Direction Determination**:
- UL channels: `UL_CCCH`, `UL_DCCH`
- DL channels: `DL_CCCH`, `DL_DCCH`, `BCCH`, `PCCH`
- GSMTAPv3: Infer from message name patterns (e.g., 'request', 'complete' → UL)

#### 3.2.2 LTE RRC Messages

**Key Patterns**:
- Message wrapper: `lte-rrc.{CHANNEL}_Message_element`
- Message tree: `lte-rrc.{channel}_Message.message_tree`
- Choice tree: `lte-rrc.c1_tree`
- Actual message: `lte-rrc.{MessageName}_element`

**Special Cases**:
- **SystemInformation**: Extract SIB types by searching for `lte-rrc.sib{N}_element` keys
- **RRCConnectionReconfiguration**: May contain nested NR RRC in `nr_SecondaryCellGroupConfig_r15_tree`

**SIB Extraction Algorithm**:
```python
def extract_sib_info(system_info_element):
    # Recursively search for sib{N}_element keys
    # Extract SIB numbers and format as "SystemInformation (SIB2 SIB3)"
    # Search depth limit: 10 levels
```

#### 3.2.3 NAS 5GS Messages

**Message Type Mapping**: Based on 3GPP TS 24.501 Tables 9.7.1 (5GMM) and 9.7.2 (5GSM)

**Key Fields**:
- 5GMM: `nas-5gs.mm.message_type` (hex code)
- 5GSM: `nas-5gs.sm.message_type` (hex code)

**Security Handling**:
- **Plain NAS**: Extract message type directly
- **Security Protected**: Check for decrypted content, otherwise label as "Security Protected NAS"

**Nested Message Extraction**:
- **UL/DL NAS Transport** (0x67, 0x68): Contains nested 5GSM messages in Payload container
- Algorithm: Navigate `Plain NAS 5GS Message` → `Payload container` → `Plain NAS 5GS Message` → message type

**Direction Mapping**:
```python
nas_5gs_messages = {
    '0x41': ('Registration Request', 'UL'),
    '0x42': ('Registration Accept', 'DL'),
    '0x67': ('UL NAS Transport', 'UL'),
    '0x68': ('DL NAS Transport', 'DL'),
    # ... (full mapping in implementation)
}
```

#### 3.2.4 NAS EPS Messages

**Message Type Mapping**: Based on 3GPP TS 24.301 Tables 9.8.1 (EMM) and 9.8.2 (ESM)

**Key Fields**:
- EMM: `nas-eps.nas_msg_emm_type` (hex code)
- ESM: `nas-eps.nas_msg_esm_type` (hex code)

**Security Handling**:
- Check `nas-eps.security_header_type`
- If non-zero and no decrypted message: "Security Protected NAS"
- If decrypted: Extract actual message type

**Direction Mapping**:
```python
nas_eps_messages = {
    '0x41': ('Attach Request', 'UL'),
    '0x42': ('Attach Accept', 'DL'),
    '0x48': ('Tracking Area Update Request', 'UL'),
    # ... (full mapping in implementation)
}
```

### 3.3 Nested Message Extraction

#### 3.3.1 NAS within RRC

**Design Decision**: Recursively search for `dedicatedNAS_Message_tree` in RRC messages.

**Search Locations**:
- `nr-rrc.dedicatedNAS_Message_tree`
- `lte-rrc.dedicatedNAS_Message_tree`

**Extraction Process**:
1. Find dedicatedNAS_Message_tree
2. Check for `nas-5gs` or `nas-eps` layer
3. Extract message type using NAS parsing logic
4. Format as "RRC Message (NAS Message)"

**Example**: `RRCReconfiguration (Registration Accept)`

#### 3.3.2 NR RRC within LTE RRC

**Design Decision**: Search for `nr_SecondaryCellGroupConfig_r15_tree` in LTE RRC messages.

**Rationale**: EN-DC (E-UTRA-NR Dual Connectivity) scenarios embed NR RRC configuration in LTE RRC messages.

**Extraction Process**:
1. Recursively search for `nr_SecondaryCellGroupConfig_r15_tree` (depth limit: 20)
2. Find NR RRC message elements within the tree
3. Extract message name
4. Format as "LTE Message (NR Message)"

**Example**: `RRCConnectionReconfiguration (RRCReconfiguration)`

#### 3.3.3 NAS within NAS Transport

**Design Decision**: Extract nested 5GSM messages from UL/DL NAS Transport.

**Extraction Process**:
1. Detect UL/DL NAS Transport (0x67, 0x68)
2. Navigate to Payload container
3. Extract nested Plain NAS 5GS Message
4. Format as "Transport Message (Nested Message)"

**Example**: `UL NAS Transport (PDU Session Establishment Request)`

### 3.4 Direction and Node Determination

#### 3.4.1 Direction Logic

**Sources of Direction Information**:
1. **Channel Type**: UL_DCCH, DL_DCCH, etc.
2. **Message Type Mapping**: From 3GPP specifications
3. **Pattern Matching**: For GSMTAPv3 messages (keywords: 'request', 'complete', 'response')

**Priority Order**:
1. Explicit channel type (highest confidence)
2. Message type mapping from specifications
3. Pattern-based inference (lowest confidence)

#### 3.4.2 Node Mapping

**Design Decision**: Map protocol + direction to source/destination nodes.

**Mapping Table**:
```
Protocol    | Direction | Source | Destination
------------|-----------|--------|------------
LTE RRC     | DL        | eNB    | UE
LTE RRC     | UL        | UE     | eNB
NR RRC      | DL        | gNB    | UE
NR RRC      | UL        | UE     | gNB
NAS EPS     | DL        | MME    | UE
NAS EPS     | UL        | UE     | MME
NAS 5GS     | DL        | AMF    | UE
NAS 5GS     | UL        | UE     | AMF
```

**Rationale**: This mapping reflects the 3GPP architecture where:
- RRC terminates at base stations (eNB/gNB)
- NAS terminates at core network (MME/AMF)

### 3.5 GSMTAPv3 Handling

**Design Decision**: Implement dual-path message extraction for GSMTAPv3.

**Rationale**: GSMTAPv3 encapsulation can place message elements at different JSON levels depending on tshark version.

**Detection Strategy**:
1. Check protocol layer for direct message elements
2. Check top-level layers for message elements
3. Use same extraction logic as standard messages

**Direction Inference**:
- Since GSMTAPv3 may not include channel information, use message name patterns
- UL patterns: 'request', 'complete', 'response', 'failure'
- DL patterns: 'accept', 'reject', 'command', 'information'
- Default: DL (most broadcast/configuration messages are DL)

### 3.6 Error Handling and Robustness

#### 3.6.1 Malformed JSON Handling

**Design Decision**: Continue processing on per-packet errors.

**Implementation**:
```python
for packet in data:
    try:
        # Extract message info
        msg_info = extract_message_info(layers)
        if msg_info['name'] == 'Unknown':
            continue  # Skip unknown messages
        # Process message
    except Exception as e:
        # Log error but continue with next packet
        continue
```

**Rationale**: One malformed packet should not prevent analysis of the entire capture.

#### 3.6.2 Unknown Message Types

**Design Decision**: Return 'Unknown' for unrecognized messages rather than crashing.

**Implementation**:
- All extraction functions return default values
- Unknown NAS types: Display hex code (e.g., "NAS-5GS 0x99")
- Unknown RRC types: Return 'Unknown'

#### 3.6.3 Debug Information Generation

**Design Decision**: Generate comprehensive debug files for troubleshooting.

**Debug Files**:
1. **{filename}_debug.txt**: tshark protocol information and text output
2. **{filename}_parse_debug.json**: Parsing statistics and sample packet analysis

**Content**:
```json
{
  "total_packets": 150,
  "parsed_flows": 142,
  "sample_debug": [
    {
      "frame": "1",
      "layers_keys": ["frame", "gsmtap", "nr-rrc"],
      "msg_info": {"protocol": "nr-rrc", "name": "RRCSetup", "direction": "DL"}
    }
  ]
}
```

### 3.7 Performance Considerations

#### 3.7.1 Large File Handling

**Design Decision**: Remove timeouts for conversion operations.

**Implementation**:
```python
subprocess.run(cmd, capture_output=True, text=True, timeout=None)
```

**Rationale**: Large captures (>100MB) can take several minutes to process. Timeouts would cause false failures.

**User Experience**:
- Display warning for files >100MB
- Show progress indicators in UI
- Reject files >2GB at upload

#### 3.7.2 Recursive Search Limits

**Design Decision**: Implement depth limits for recursive searches.

**Limits**:
- SIB extraction: 10 levels
- Nested NAS extraction: Implicit (single-level recursion)
- Nested NR RRC extraction: 20 levels

**Rationale**: Prevents infinite loops on malformed data while allowing deep nesting in legitimate messages.

### 3.8 Timestamp Formatting

**Design Decision**: Extract and format timestamps consistently.

**Format**: `HH:MM:SS.mmm` (3-digit milliseconds)

**Implementation**:
```python
def format_timestamp(timestamp_full):
    # Input: "Jan 27, 2026 16:43:13.790560000 KST"
    # Output: "16:43:13.790"
    match = re.search(r'(\d{2}):(\d{2}):(\d{2})\.(\d+)', timestamp_full)
    if match:
        hh, mm, ss, ms = match.groups()
        return f"{hh}:{mm}:{ss}.{ms[:3]}"
```

**Rationale**: Consistent format improves readability and allows correlation with external logs.

## 4. Data Structures

### 4.1 Message Info Object

```python
{
    'protocol': str,      # 'lte-rrc', 'nr-rrc', 'nas-5gs', 'nas-eps'
    'name': str,          # Message name (e.g., 'RRCReconfiguration')
    'raw_key': str,       # Original JSON key
    'direction': str,     # 'UL' or 'DL'
    'channel': str        # Channel type (e.g., 'DL_DCCH_Message')
}
```

### 4.2 Call Flow Object

```python
{
    'frame': str,         # Frame number
    'timestamp': str,     # Formatted timestamp (HH:MM:SS.mmm)
    'source': str,        # Source node (UE, eNB, gNB, MME, AMF)
    'destination': str,   # Destination node
    'direction': str,     # 'UL' or 'DL'
    'message': str,       # Message name (may include nested messages)
    'protocol': str,      # Protocol type
    'details': dict       # Full JSON layers for detail view
}
```

## 5. UI Design

### 5.1 Call Flow Diagram

**Layout**: 5-column node display
- Columns: UE | eNB | MME | gNB | AMF
- Vertical dashed lines for each node
- Horizontal arrows for messages

**Arrow Styling**:
- Blue: UL messages
- Red: DL messages
- Label: Message name above arrow
- Nested messages: Smaller font in parentheses

**Example**:
```
UE          eNB         MME         gNB         AMF
|            |           |           |           |
|----------->|                                   |  RRCConnectionRequest
|<-----------|                                   |  RRCConnectionSetup
|----------->|                                   |  RRCConnectionSetupComplete (Attach Request)
```

### 5.2 Message Details Panel

**Trigger**: Click on message arrow

**Content**:
- **Header**: Frame number, timestamp, protocol
- **Basic Info**: Source, destination, direction
- **IE Tree**: JSON tree view with syntax highlighting

**IE Tree Rendering**:
- Keys: Blue color
- Strings: Green color
- Numbers: Orange color
- Booleans: Purple color
- Collapsible nested objects

**String Reconstruction**:
- tshark splits long strings into indexed objects
- Reconstruct: `{"0": "abc", "1": "def"}` → `"abcdef"`

## 6. Testing Strategy

### 6.1 Unit Tests

**Test Coverage**:
- Message extraction for each protocol type
- Direction determination logic
- Nested message extraction
- Layer key normalization
- Timestamp formatting

**Test Data**: Synthetic JSON structures representing various message types

### 6.2 Integration Tests

**Test Scenarios**:
1. QMDL → PCAP → JSON → Call Flow (full pipeline)
2. Direct PCAP upload
3. Large file processing (>100MB)
4. Malformed JSON handling
5. Unknown message types

**Test Files**: Real-world captures from LTE and 5G networks

### 6.3 Property-Based Tests

**Properties to Test**:
1. **Parsing Completeness**: All packets with RRC/NAS layers produce flow entries
2. **Direction Consistency**: UL messages always have UE as source
3. **Node Mapping**: Protocol + direction always maps to valid node pair
4. **Nested Message Format**: Nested messages always follow "Parent (Nested)" format

**Test Framework**: Python `hypothesis` library

**Example Property**:
```python
@given(protocol=st.sampled_from(['lte-rrc', 'nr-rrc', 'nas-5gs', 'nas-eps']),
       direction=st.sampled_from(['UL', 'DL']))
def test_node_mapping_valid(protocol, direction):
    _, source, dest = determine_direction_and_nodes({'protocol': protocol, 'direction': direction})
    assert source in ['UE', 'eNB', 'gNB', 'MME', 'AMF']
    assert dest in ['UE', 'eNB', 'gNB', 'MME', 'AMF']
    assert source != dest
```

## 7. Backward Compatibility

### 7.1 Compatibility Requirements

**Must Maintain**:
- Existing API endpoints (`/`, `/upload`)
- JSON response format
- UI component structure
- File storage locations

**Allowed Changes**:
- Internal parsing logic
- Message extraction algorithms
- Debug file formats

### 7.2 Migration Strategy

**Approach**: In-place enhancement (no migration needed)

**Validation**:
- Test with existing sample files
- Verify output format unchanged
- Ensure UI continues to render correctly

## 8. Dependencies

### 8.1 External Tools

**scat**:
- Purpose: QMDL/HDF → PCAP conversion
- Version: Any recent version
- Installation: Platform-specific

**tshark**:
- Purpose: PCAP → JSON conversion
- Version: 3.0+ (for JSON output support)
- Installation: Part of Wireshark package

### 8.2 Python Libraries

**Flask**: 3.0.0
- Web framework
- File upload handling

**Werkzeug**: 3.0.1
- Secure filename handling
- HTTP utilities

**Standard Library**:
- `json`: JSON parsing
- `subprocess`: External tool execution
- `re`: Timestamp parsing
- `os`: File operations

## 9. Security Considerations

### 9.1 File Upload Security

**Measures**:
- Filename sanitization via `secure_filename()`
- File size limit: 2GB
- Allowed extensions: QMDL, HDF, PCAP only
- Files stored in isolated directories

### 9.2 Command Injection Prevention

**Measures**:
- Use subprocess with argument lists (not shell=True)
- No user input in command construction
- Sanitized filenames only

**Example**:
```python
# Safe: Arguments as list
subprocess.run(['tshark', '-r', pcap_path, '-T', 'json'], ...)

# Unsafe: Shell command with user input (NOT USED)
# subprocess.run(f'tshark -r {user_file}', shell=True)
```

### 9.3 JSON Parsing Safety

**Measures**:
- Validate JSON before parsing
- Handle parsing exceptions gracefully
- Limit recursion depth in nested searches

## 10. Future Enhancements

### 10.1 Potential Improvements

1. **Real-time Capture**: Support live packet capture via tshark
2. **Message Filtering**: Allow users to filter by protocol, message type, or time range
3. **Export Functionality**: Export call flow as PDF or image
4. **Message Search**: Full-text search across message names and IEs
5. **Sequence Validation**: Validate message sequences against 3GPP procedures
6. **Performance Optimization**: Parallel processing for large files

### 10.2 Protocol Extensions

1. **S1AP/NGAP**: Add core network signaling protocols
2. **PDCP/RLC**: Add lower layer protocols
3. **SIP/IMS**: Add voice call signaling
4. **X2/Xn**: Add inter-base-station signaling

## 11. Correctness Properties

### 11.1 Message Extraction Properties

**Property 1.1: Protocol Layer Detection**
- **Specification**: For any packet containing an RRC or NAS protocol layer, the parser SHALL identify the protocol type
- **Validates**: Requirements 3, 4, 7, 8
- **Test Strategy**: Generate packets with various protocol layers and verify detection

**Property 1.2: Message Name Extraction**
- **Specification**: For any valid RRC/NAS message, the parser SHALL extract a non-empty message name
- **Validates**: Requirements 3, 4, 7, 8
- **Test Strategy**: Verify all parsed messages have non-'Unknown' names for valid input

**Property 1.3: Layer Key Normalization**
- **Specification**: The parser SHALL correctly identify protocol layers regardless of hyphen or underscore format
- **Validates**: Requirement 6
- **Test Strategy**: Test same message with both 'lte-rrc' and 'lte_rrc' keys

### 11.2 Direction and Node Properties

**Property 2.1: Direction Consistency**
- **Specification**: For any UL message, source SHALL be 'UE'; for any DL message, destination SHALL be 'UE'
- **Validates**: Requirements 9, 10
- **Test Strategy**: Verify all parsed messages satisfy this invariant

**Property 2.2: Node Validity**
- **Specification**: Source and destination nodes SHALL always be from the set {UE, eNB, gNB, MME, AMF}
- **Validates**: Requirement 10
- **Test Strategy**: Check all parsed messages have valid node values

**Property 2.3: Node Distinctness**
- **Specification**: Source and destination SHALL never be the same node
- **Validates**: Requirement 10
- **Test Strategy**: Verify source ≠ destination for all messages

### 11.3 Nested Message Properties

**Property 3.1: Nested Message Format**
- **Specification**: When a nested message is found, the format SHALL be "Parent (Nested)"
- **Validates**: Requirements 13, 3.8, 4.7
- **Test Strategy**: Verify all messages with nested content follow this format

**Property 3.2: Nested Message Extraction**
- **Specification**: For RRC messages containing dedicatedNAS_Message_tree, the parser SHALL extract the NAS message name
- **Validates**: Requirement 13
- **Test Strategy**: Test with RRC messages containing NAS and verify extraction

### 11.4 GSMTAPv3 Properties

**Property 4.1: GSMTAPv3 Message Extraction**
- **Specification**: Messages encapsulated in GSMTAPv3 SHALL be extracted with the same accuracy as non-encapsulated messages
- **Validates**: Requirement 5
- **Test Strategy**: Compare extraction results for same message with/without GSMTAPv3

**Property 4.2: GSMTAPv3 Direction Inference**
- **Specification**: For GSMTAPv3 messages without explicit channel info, direction SHALL be inferred from message name patterns
- **Validates**: Requirements 5, 9
- **Test Strategy**: Verify direction inference matches expected patterns

### 11.5 Error Handling Properties

**Property 5.1: Graceful Degradation**
- **Specification**: Parser SHALL continue processing remaining packets when encountering an unparseable packet
- **Validates**: Requirement 16
- **Test Strategy**: Insert malformed packet in middle of valid packets, verify others are parsed

**Property 5.2: Unknown Message Handling**
- **Specification**: Parser SHALL return 'Unknown' for unrecognized messages without crashing
- **Validates**: Requirement 16
- **Test Strategy**: Test with fabricated unknown message types

### 11.6 Timestamp Properties

**Property 6.1: Timestamp Format Consistency**
- **Specification**: All timestamps SHALL follow the format HH:MM:SS.mmm
- **Validates**: Requirement 17
- **Test Strategy**: Verify all parsed timestamps match regex `\d{2}:\d{2}:\d{2}\.\d{3}`

**Property 6.2: Timestamp Ordering**
- **Specification**: Timestamps SHALL maintain chronological order from input
- **Validates**: Requirement 17
- **Test Strategy**: Verify parsed timestamps are monotonically increasing

### 11.7 Completeness Properties

**Property 7.1: LTE RRC Coverage**
- **Specification**: Parser SHALL extract all LTE RRC message types defined in 3GPP TS 36.331
- **Validates**: Requirement 3
- **Test Strategy**: Test with comprehensive set of LTE RRC messages

**Property 7.2: NR RRC Coverage**
- **Specification**: Parser SHALL extract all NR RRC message types defined in 3GPP TS 38.331
- **Validates**: Requirement 4
- **Test Strategy**: Test with comprehensive set of NR RRC messages

**Property 7.3: NAS 5GS Coverage**
- **Specification**: Parser SHALL correctly map all NAS 5GS message types from 3GPP TS 24.501 Tables 9.7.1 and 9.7.2
- **Validates**: Requirement 7
- **Test Strategy**: Test with all message type hex codes from specification

**Property 7.4: NAS EPS Coverage**
- **Specification**: Parser SHALL correctly map all NAS EPS message types from 3GPP TS 24.301 Tables 9.8.1 and 9.8.2
- **Validates**: Requirement 8
- **Test Strategy**: Test with all message type hex codes from specification

## 12. Implementation Notes

### 12.1 Code Organization

**File Structure**:
- `app.py`: All parsing logic and Flask routes
- `templates/index.html`: UI and visualization
- No separate modules (keep simple for maintainability)

**Function Organization**:
- Conversion functions: `convert_to_pcap()`, `convert_pcap_to_json()`
- Parsing functions: `parse_call_flow()`, `extract_message_info()`
- Helper functions: `extract_nested_*()`, `get_nas_*_message_name()`
- Utility functions: `format_timestamp()`, `determine_direction_and_nodes()`

### 12.2 Coding Standards

**Style**:
- Function names: snake_case
- Variable names: snake_case
- Comments: Korean language
- Docstrings: Korean language

**Error Handling**:
- Use try-except blocks for external tool calls
- Log errors with context information
- Return meaningful error messages to user

### 12.3 Debug Output

**Debug Files**:
- Always generate debug files for troubleshooting
- Include sample data (first 5 packets)
- Save to same directory as output files

**Logging**:
- Print progress information to console
- Include file sizes and processing times
- Log errors with full stack traces

## 13. Acceptance Criteria Summary

This design addresses all 20 requirements from the requirements document:

1. ✓ File upload and conversion pipeline (Req 1)
2. ✓ PCAP to JSON conversion (Req 2)
3. ✓ LTE RRC message parsing (Req 3)
4. ✓ NR RRC message parsing (Req 4)
5. ✓ GSMTAPv3 handling (Req 5)
6. ✓ Multiple layer key formats (Req 6)
7. ✓ NAS 5GS message parsing (Req 7)
8. ✓ NAS EPS message parsing (Req 8)
9. ✓ Message direction identification (Req 9)
10. ✓ Source/destination node determination (Req 10)
11. ✓ Interactive call flow diagram (Req 11)
12. ✓ Message details panel (Req 12)
13. ✓ Nested message extraction (Req 13)
14. ✓ Message tree structure navigation (Req 14)
15. ✓ Debug information generation (Req 15)
16. ✓ Backward compatibility (Req 16)
17. ✓ Timestamp formatting (Req 17)
18. ✓ Large file handling (Req 18)
19. ✓ Dependency validation (Req 19)
20. ✓ SystemInformation SIB extraction (Req 20)

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-28 | System | Initial design document |
