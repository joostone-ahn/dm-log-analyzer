# Implementation Tasks: RRC Parsing Accuracy Enhancement

## Status Legend
- `[ ]` Not started
- `[~]` Queued
- `[-]` In progress
- `[x]` Completed

## 1. Core Message Parsing Enhancement

### 1.1 LTE RRC Message Parsing
- [x] 1.1.1 Implement LTE RRC message extraction with Message_element pattern (Validates: Req 3.1-3.6)
- [x] 1.1.2 Implement LTE RRC c1_tree navigation for actual message types (Validates: Req 3.1-3.6)
- [x] 1.1.3 Implement SystemInformation SIB extraction with recursive search (Validates: Req 3.5, 20)
- [x] 1.1.4 Add support for nested NAS messages in LTE RRC (Validates: Req 3.7)
- [x] 1.1.5 Add support for nested NR RRC messages in LTE RRC (Validates: Req 3.8)

### 1.2 NR RRC Message Parsing
- [x] 1.2.1 Implement NR RRC message extraction with Message_element pattern (Validates: Req 4.1-4.6)
- [x] 1.2.2 Implement NR RRC c1_tree navigation for actual message types (Validates: Req 4.1-4.6)
- [x] 1.2.3 Add special handling for MIB messages in BCCH_BCH_Message (Validates: Req 4.4)
- [x] 1.2.4 Add special handling for SystemInformationBlockType1 (Validates: Req 4.5)
- [x] 1.2.5 Add support for nested NAS messages in NR RRC (Validates: Req 4.7)

### 1.3 GSMTAPv3 Encapsulation Support
- [x] 1.3.1 Implement direct message element extraction for GSMTAPv3 (Validates: Req 5.1-5.3)
- [x] 1.3.2 Implement top-level layer search for GSMTAPv3 messages (Validates: Req 5.5)
- [ ] 1.3.3 Write property-based test for GSMTAPv3 message extraction accuracy (Validates: Property 4.1)
  - Test that GSMTAPv3 encapsulated messages are extracted with same accuracy as non-encapsulated
  - Use hypothesis to generate test cases with both encapsulation types
  - **Validates: Requirements 5.1-5.4, Design Property 4.1**

### 1.4 Layer Key Normalization
- [x] 1.4.1 Implement hyphen variant support (lte-rrc, nr-rrc, nas-5gs, nas-eps) (Validates: Req 6.1)
- [x] 1.4.2 Implement underscore variant support (lte_rrc, nr_rrc, nas_5gs, nas_eps) (Validates: Req 6.2)
- [x] 1.4.3 Add dual-check logic for both variants in all parsing functions (Validates: Req 6.3)
- [ ] 1.4.4 Write property-based test for layer key normalization (Validates: Property 1.3)
  - Test that both hyphen and underscore variants produce identical results
  - Use hypothesis to generate test packets with both key formats
  - **Validates: Requirements 6.1-6.4, Design Property 1.3**

## 2. NAS Message Parsing

### 2.1 NAS 5GS Message Support
- [x] 2.1.1 Implement complete NAS 5GS message type mapping from 3GPP TS 24.501 (Validates: Req 7.1-7.2)
- [x] 2.1.2 Add security protected NAS message detection (Validates: Req 7.3)
- [x] 2.1.3 Add plain NAS message extraction (Validates: Req 7.4)
- [x] 2.1.4 Implement nested NAS extraction from UL/DL NAS Transport (Validates: Req 7.5)
- [x] 2.1.5 Add unknown message type hex code display (Validates: Req 7.6)
- [x] 2.1.6 Implement direction mapping from 3GPP TS 24.501 (Validates: Req 7.7)
- [ ] 2.1.7 Write property-based test for NAS 5GS message coverage (Validates: Property 7.3)
  - Test all message type hex codes from 3GPP TS 24.501 Tables 9.7.1 and 9.7.2
  - Verify correct message name and direction for each code
  - **Validates: Requirements 7.1-7.7, Design Property 7.3**

### 2.2 NAS EPS Message Support
- [x] 2.2.1 Implement complete NAS EPS message type mapping from 3GPP TS 24.301 (Validates: Req 8.1-8.2)
- [x] 2.2.2 Add security protected NAS message detection with decryption check (Validates: Req 8.3-8.4)
- [x] 2.2.3 Add unknown message type hex code display (Validates: Req 8.5)
- [x] 2.2.4 Implement direction mapping from 3GPP TS 24.301 (Validates: Req 8.6)
- [ ] 2.2.5 Write property-based test for NAS EPS message coverage (Validates: Property 7.4)
  - Test all message type hex codes from 3GPP TS 24.301 Tables 9.8.1 and 9.8.2
  - Verify correct message name and direction for each code
  - **Validates: Requirements 8.1-8.6, Design Property 7.4**

## 3. Direction and Node Determination

### 3.1 Direction Identification
- [x] 3.1.1 Implement channel-based direction detection (UL_DCCH, DL_DCCH, etc.) (Validates: Req 9.1-9.5)
- [x] 3.1.2 Implement BCCH/PCCH downlink direction handling (Validates: Req 9.5)
- [x] 3.1.3 Add GSMTAPv3 direction inference from message patterns (Validates: Req 9.6)
- [x] 3.1.4 Use NAS message type mapping for direction (Validates: Req 9.7)
- [ ] 3.1.5 Write property-based test for direction consistency (Validates: Property 2.1)
  - Test that all UL messages have UE as source
  - Test that all DL messages have UE as destination
  - Use hypothesis to generate various message types
  - **Validates: Requirements 9.1-9.7, Design Property 2.1**

### 3.2 Node Mapping
- [x] 3.2.1 Implement LTE RRC node mapping (eNB ↔ UE) (Validates: Req 10.1-10.2)
- [x] 3.2.2 Implement NR RRC node mapping (gNB ↔ UE) (Validates: Req 10.3-10.4)
- [x] 3.2.3 Implement NAS EPS node mapping (MME ↔ UE) (Validates: Req 10.5-10.6)
- [x] 3.2.4 Implement NAS 5GS node mapping (AMF ↔ UE) (Validates: Req 10.7-10.8)
- [ ] 3.2.5 Write property-based test for node validity and distinctness (Validates: Properties 2.2, 2.3)
  - Test that all nodes are from valid set {UE, eNB, gNB, MME, AMF}
  - Test that source ≠ destination for all messages
  - Use hypothesis to generate protocol and direction combinations
  - **Validates: Requirements 10.1-10.8, Design Properties 2.2, 2.3**

## 4. Nested Message Extraction

### 4.1 NAS within RRC
- [x] 4.1.1 Implement dedicatedNAS_Message_tree search in RRC messages (Validates: Req 13.1)
- [x] 4.1.2 Extract NAS 5GS messages from RRC (Validates: Req 13.1)
- [x] 4.1.3 Extract NAS EPS messages from RRC (Validates: Req 13.1)
- [x] 4.1.4 Format nested messages as "Parent (Nested)" (Validates: Req 13.6)
- [ ] 4.1.5 Write property-based test for nested NAS extraction (Validates: Property 3.2)
  - Test that RRC messages with dedicatedNAS_Message_tree extract NAS correctly
  - Verify "Parent (Nested)" format
  - **Validates: Requirements 13.1, 13.6, Design Property 3.2**

### 4.2 NR RRC within LTE RRC
- [x] 4.2.1 Implement nr_SecondaryCellGroupConfig_r15_tree search (Validates: Req 13.3)
- [x] 4.2.2 Extract NR RRC message names from LTE RRC (Validates: Req 13.3)
- [x] 4.2.3 Format nested messages as "Parent (Nested)" (Validates: Req 13.6)
- [ ] 4.2.4 Write property-based test for nested NR RRC extraction (Validates: Property 3.2)
  - Test EN-DC scenarios with nested NR RRC in LTE RRC
  - Verify correct extraction and format
  - **Validates: Requirements 13.3, 13.6, Design Property 3.2**

### 4.3 NAS within NAS Transport
- [x] 4.3.1 Implement Payload container navigation for UL/DL NAS Transport (Validates: Req 13.2)
- [x] 4.3.2 Extract nested 5GSM messages from transport messages (Validates: Req 13.2)
- [x] 4.3.3 Format nested messages as "Transport (Nested)" (Validates: Req 13.6)
- [ ] 4.3.4 Write property-based test for nested message format (Validates: Property 3.1)
  - Test that all nested messages follow "Parent (Nested)" format
  - Use hypothesis to generate various nested message combinations
  - **Validates: Requirements 13.2, 13.6, Design Property 3.1**

### 4.4 Recursive Search Implementation
- [x] 4.4.1 Implement recursive tree navigation with depth limits (Validates: Req 14.1-14.4)
- [x] 4.4.2 Add message_tree navigation (Validates: Req 14.1)
- [x] 4.4.3 Add c1_tree navigation (Validates: Req 14.2)
- [x] 4.4.4 Add criticalExtensions_tree navigation (Validates: Req 14.3)
- [x] 4.4.5 Implement graceful handling of search failures (Validates: Req 13.5)

## 5. File Processing Pipeline

### 5.1 File Upload and Validation
- [x] 5.1.1 Implement QMDL file upload handling (Validates: Req 1.1)
- [x] 5.1.2 Implement HDF file upload handling (Validates: Req 1.2)
- [x] 5.1.3 Implement direct PCAP file upload (Validates: Req 1.3)
- [x] 5.1.4 Add file size validation (2GB limit) (Validates: Req 1.6)
- [x] 5.1.5 Add loading indicator display (Validates: Req 1.4)
- [x] 5.1.6 Add error message display for conversion failures (Validates: Req 1.5)

### 5.2 Dependency Management
- [x] 5.2.1 Implement scat installation check (Validates: Req 19.1, 19.3)
- [x] 5.2.2 Implement tshark installation check (Validates: Req 19.2, 19.4)
- [x] 5.2.3 Add timeout handling for dependency checks (Validates: Req 19.5)
- [x] 5.2.4 Display dependency error messages (Validates: Req 1.7)

### 5.3 PCAP Conversion
- [x] 5.3.1 Implement scat conversion with no timeout (Validates: Req 2.5, 18.2)
- [x] 5.3.2 Add PCAP file validation after conversion (Validates: Req 2.1)
- [x] 5.3.3 Add empty file detection (Validates: Req 2.1)
- [x] 5.3.4 Capture and display scat stderr output (Validates: Req 2.6)

### 5.4 JSON Conversion
- [x] 5.4.1 Implement tshark JSON conversion with no timeout (Validates: Req 2.1, 18.3)
- [x] 5.4.2 Add JSON validation after conversion (Validates: Req 2.2)
- [x] 5.4.3 Save debug information on JSON errors (Validates: Req 2.3)
- [x] 5.4.4 Save JSON file to jsons/ directory (Validates: Req 2.4)
- [x] 5.4.5 Capture and include tshark stderr in errors (Validates: Req 2.6)

### 5.5 Large File Handling
- [x] 5.5.1 Display warning for files >100MB (Validates: Req 18.1)
- [x] 5.5.2 Remove timeout restrictions for large files (Validates: Req 18.2-18.3)
- [x] 5.5.3 Display progress information during processing (Validates: Req 18.4)
- [x] 5.5.4 Reject files >2GB before processing (Validates: Req 18.5)

## 6. UI and Visualization

### 6.1 Call Flow Diagram
- [x] 6.1.1 Implement 5-column node display (UE, eNB, MME, gNB, AMF) (Validates: Req 11.1)
- [x] 6.1.2 Draw arrows from source to destination (Validates: Req 11.2)
- [x] 6.1.3 Color UL messages blue (Validates: Req 11.3)
- [x] 6.1.4 Color DL messages red (Validates: Req 11.4)
- [x] 6.1.5 Display message name as label above arrow (Validates: Req 11.5)
- [x] 6.1.6 Display nested messages in smaller font with parentheses (Validates: Req 11.6)
- [x] 6.1.7 Format timestamps as HH:MM:SS.mmm (Validates: Req 11.7, 17.2)
- [x] 6.1.8 Display vertical dashed lines for node columns (Validates: Req 11.8)
- [x] 6.1.9 Display total message count (Validates: Req 11.9)

### 6.2 Message Details Panel
- [x] 6.2.1 Implement click handler to open details panel (Validates: Req 12.1)
- [x] 6.2.2 Display basic information (frame, timestamp, protocol, direction, nodes) (Validates: Req 12.2)
- [x] 6.2.3 Display full IE tree structure in JSON format (Validates: Req 12.3)
- [x] 6.2.4 Add syntax highlighting for JSON (keys, strings, numbers, booleans) (Validates: Req 12.4)
- [x] 6.2.5 Display only relevant protocol layer data (Validates: Req 12.5)
- [x] 6.2.6 Add Escape key handler to close panel (Validates: Req 12.6)
- [x] 6.2.7 Add close button click handler (Validates: Req 12.7)
- [x] 6.2.8 Reconstruct split strings from indexed objects (Validates: Req 12.8)

### 6.3 Timestamp Formatting
- [x] 6.3.1 Extract time portion from full timestamp (Validates: Req 17.1)
- [x] 6.3.2 Format as HH:MM:SS.mmm with 3-digit milliseconds (Validates: Req 17.2)
- [x] 6.3.3 Return original string on parsing failure (Validates: Req 17.3)
- [x] 6.3.4 Align timestamps consistently in time column (Validates: Req 17.4)
- [ ] 6.3.5 Write property-based test for timestamp format consistency (Validates: Property 6.1)
  - Test that all timestamps match HH:MM:SS.mmm format
  - Use hypothesis to generate various timestamp inputs
  - **Validates: Requirements 17.1-17.4, Design Property 6.1**

## 7. Error Handling and Robustness

### 7.1 Malformed Data Handling
- [x] 7.1.1 Implement per-packet error handling with continue (Validates: Req 16.1)
- [x] 7.1.2 Skip unknown messages without crashing (Validates: Req 16.2)
- [x] 7.1.3 Return 'Unknown' for unrecognized message types (Validates: Req 16.3)
- [x] 7.1.4 Handle malformed JSON gracefully (Validates: Req 16.4)
- [x] 7.1.5 Continue processing remaining packets on errors (Validates: Req 16.5)
- [ ] 7.1.6 Write property-based test for graceful degradation (Validates: Property 5.1)
  - Test that parser continues after encountering unparseable packet
  - Insert malformed packets in middle of valid packets
  - **Validates: Requirements 16.1-16.5, Design Property 5.1**

### 7.2 Debug Information Generation
- [x] 7.2.1 Generate tshark debug file with protocol information (Validates: Req 15.1)
- [x] 7.2.2 Generate parse debug JSON file (Validates: Req 15.2)
- [x] 7.2.3 Include total packet count and parsed flow count (Validates: Req 15.3)
- [x] 7.2.4 Include sample debug info for first 5 packets (Validates: Req 15.4)
- [x] 7.2.5 Save error details to debug files (Validates: Req 15.5)
- [x] 7.2.6 Use naming pattern {base_name}_debug.txt and {base_name}_parse_debug.json (Validates: Req 15.6)

## 8. Testing and Validation

### 8.1 Unit Tests
- [ ]* 8.1.1 Write unit tests for extract_message_info() with synthetic JSON
  - Test each protocol type (LTE RRC, NR RRC, NAS 5GS, NAS EPS)
  - Test various message types and structures
  - **Validates: Requirements 3, 4, 7, 8**

- [ ]* 8.1.2 Write unit tests for determine_direction_and_nodes()
  - Test all protocol and direction combinations
  - Verify correct node mapping
  - **Validates: Requirements 9, 10**

- [ ]* 8.1.3 Write unit tests for nested message extraction functions
  - Test extract_nested_nas_message()
  - Test extract_nested_nr_rrc_message()
  - Test extract_nested_nas_from_transport()
  - **Validates: Requirements 13**

- [ ]* 8.1.4 Write unit tests for timestamp formatting
  - Test various timestamp formats
  - Test edge cases and error handling
  - **Validates: Requirements 17**

### 8.2 Integration Tests
- [ ]* 8.2.1 Test full pipeline with real QMDL files
  - Test QMDL → PCAP → JSON → Call Flow
  - Verify output correctness
  - **Validates: Requirements 1, 2**

- [ ]* 8.2.2 Test direct PCAP upload
  - Skip scat conversion
  - Verify JSON conversion and parsing
  - **Validates: Requirements 1.3, 2**

- [ ]* 8.2.3 Test large file processing (>100MB)
  - Verify timeout handling
  - Verify progress indicators
  - **Validates: Requirements 18**

- [ ]* 8.2.4 Test malformed JSON handling
  - Test with corrupted JSON files
  - Verify graceful error handling
  - **Validates: Requirements 16**

- [ ]* 8.2.5 Test unknown message types
  - Test with fabricated unknown messages
  - Verify 'Unknown' return without crash
  - **Validates: Requirements 16**

### 8.3 Property-Based Tests (REQUIRED)
- [ ] 8.3.1 Write property test for parsing completeness (Validates: Design Section 11.1)
  - Property: All packets with RRC/NAS layers produce flow entries
  - Use hypothesis to generate various packet structures
  - **Validates: Requirements 3, 4, 7, 8, Design Property 7.1, 7.2**

- [ ] 8.3.2 Write property test for message extraction (Validates: Property 1.2)
  - Property: All valid RRC/NAS messages have non-'Unknown' names
  - Use hypothesis to generate valid message structures
  - **Validates: Requirements 3, 4, 7, 8, Design Property 1.2**

## 9. Documentation and Cleanup

### 9.1 Code Documentation
- [ ]* 9.1.1 Add comprehensive docstrings to all functions
  - Include parameter descriptions
  - Include return value descriptions
  - Include example usage where helpful

- [ ]* 9.1.2 Add inline comments for complex logic
  - Explain recursive search algorithms
  - Explain nested message extraction
  - Explain GSMTAPv3 handling

### 9.2 Backward Compatibility Validation
- [ ]* 9.2.1 Test with existing sample files
  - Verify output format unchanged
  - Verify UI continues to render correctly
  - **Validates: Requirements 16.1-16.2**

- [ ]* 9.2.2 Validate API endpoint compatibility
  - Test / and /upload endpoints
  - Verify JSON response format
  - **Validates: Requirements 16**

## Notes

- Tasks marked with `*` are optional enhancements
- Property-based tests (Section 8.3) are REQUIRED and must be implemented
- All property tests should use Python's `hypothesis` library
- Focus on completing required tasks before optional tasks
- Each task should be tested individually before moving to the next
- Debug files should be generated for all processing steps to aid troubleshooting
