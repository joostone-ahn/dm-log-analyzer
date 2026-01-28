# Requirements Document

## Introduction

This document specifies the requirements for the QMDL Call Flow Analyzer, a web-based telecom protocol analysis tool. The system processes QMDL/HDF/PCAP files containing LTE/NR RRC and NAS messages, converts them through a pipeline (QMDL → PCAP → JSON), and displays the protocol messages in an interactive call flow diagram.

The application serves telecom engineers who need to analyze 4G/5G network protocol sequences, debug call flows, and verify RRC/NAS message exchanges between network nodes (UE, eNB, gNB, MME, AMF).

## Glossary

- **QMDL**: Qualcomm Diagnostic Monitor Log format, a binary log file format from Qualcomm chipsets
- **HDF**: Hierarchical Data Format, another log file format used in telecom testing
- **PCAP**: Packet Capture format, standard network packet capture file format
- **scat**: External tool that converts QMDL/HDF files to PCAP format
- **tshark**: Wireshark command-line tool that converts PCAP to JSON format
- **RRC**: Radio Resource Control protocol used in LTE and NR (5G) networks
- **NAS**: Non-Access Stratum protocol for mobility management and session management
- **LTE_RRC**: Long-Term Evolution Radio Resource Control messages
- **NR_RRC**: New Radio (5G) Radio Resource Control messages
- **NAS_EPS**: NAS protocol for 4G/LTE networks (EMM and ESM messages)
- **NAS_5GS**: NAS protocol for 5G networks (5GMM and 5GSM messages)
- **Call_Flow**: Visual diagram showing message sequence between network nodes
- **Network_Nodes**: UE (User Equipment), eNB (LTE base station), gNB (5G base station), MME (LTE core), AMF (5G core)
- **Message_Direction**: UL (uplink from UE) or DL (downlink to UE)
- **IE**: Information Element, the structured data fields within protocol messages
- **GSMTAPv3**: GSMTAP version 3 protocol encapsulation layer that can wrap RRC messages

## Requirements

### Requirement 1: File Upload and Conversion Pipeline

**User Story:** As a telecom engineer, I want to upload QMDL, HDF, or PCAP files through a web interface, so that I can analyze protocol messages without manual conversion steps.

#### Acceptance Criteria

1. WHEN a user uploads a QMDL file, THE System SHALL convert it to PCAP using scat tool
2. WHEN a user uploads an HDF file, THE System SHALL convert it to PCAP using scat tool
3. WHEN a user uploads a PCAP file directly, THE System SHALL skip the scat conversion step
4. WHEN a file is uploaded, THE System SHALL display a loading indicator with progress information
5. WHEN conversion fails, THE System SHALL display a clear error message to the user
6. WHEN a file exceeds 2GB, THE System SHALL reject the upload with an appropriate error message
7. WHEN scat or tshark is not installed, THE System SHALL display a dependency error message

### Requirement 2: PCAP to JSON Conversion

**User Story:** As a developer, I want PCAP files to be converted to JSON format using tshark, so that protocol messages can be parsed programmatically.

#### Acceptance Criteria

1. WHEN a PCAP file is available, THE System SHALL convert it to JSON using tshark
2. WHEN tshark conversion completes, THE System SHALL validate the JSON output
3. WHEN JSON is invalid, THE System SHALL save debug information and return an error
4. WHEN conversion succeeds, THE System SHALL save the JSON file to the jsons/ directory
5. WHEN processing large files, THE System SHALL run tshark without timeout restrictions
6. WHEN tshark fails, THE System SHALL capture stderr output and include it in the error message

### Requirement 3: Parse All LTE RRC Messages

**User Story:** As a telecom engineer, I want all LTE RRC messages to be parsed from PCAP files, so that I can analyze complete LTE call flows without missing messages.

#### Acceptance Criteria

1. WHEN a PCAP file contains RRCConnectionReconfiguration messages, THE Parser SHALL extract and identify them correctly
2. WHEN a PCAP file contains RRCConnectionSetup messages, THE Parser SHALL extract and identify them correctly
3. WHEN a PCAP file contains RRCConnectionRequest messages, THE Parser SHALL extract and identify them correctly
4. WHEN a PCAP file contains RRCConnectionRelease messages, THE Parser SHALL extract and identify them correctly
5. WHEN a PCAP file contains SystemInformation messages, THE Parser SHALL extract them and identify the SIB types
6. WHEN a PCAP file contains any valid LTE RRC message type, THE Parser SHALL extract and identify it correctly
7. WHEN an LTE RRC message contains nested NAS messages, THE Parser SHALL extract both RRC and NAS message names
8. WHEN an LTE RRC message contains nested NR RRC messages, THE Parser SHALL extract both LTE and NR message names

### Requirement 4: Parse All NR RRC Messages

**User Story:** As a telecom engineer, I want all NR (5G) RRC messages to be parsed from PCAP files, so that I can analyze complete 5G call flows without missing messages.

#### Acceptance Criteria

1. WHEN a PCAP file contains RRCReconfiguration messages, THE Parser SHALL extract and identify them correctly
2. WHEN a PCAP file contains RRCSetup messages, THE Parser SHALL extract and identify them correctly
3. WHEN a PCAP file contains RRCRequest messages, THE Parser SHALL extract and identify them correctly
4. WHEN a PCAP file contains MIB (Master Information Block) messages, THE Parser SHALL extract and identify them correctly
5. WHEN a PCAP file contains SystemInformationBlockType1 messages, THE Parser SHALL extract and identify them correctly
6. WHEN a PCAP file contains any valid NR RRC message type, THE Parser SHALL extract and identify it correctly
7. WHEN an NR RRC message contains nested NAS messages, THE Parser SHALL extract both RRC and NAS message names

### Requirement 5: Handle GSMTAPv3 Encapsulated Messages

**User Story:** As a telecom engineer, I want RRC messages wrapped in GSMTAPv3 protocol to be parsed correctly, so that I can analyze messages from all capture sources.

#### Acceptance Criteria

1. WHEN an RRC message is encapsulated in GSMTAPv3 protocol, THE Parser SHALL extract the underlying RRC message correctly
2. WHEN a GSMTAPv3 packet contains RRCReconfiguration, THE Parser SHALL identify it as RRCReconfiguration
3. WHEN a GSMTAPv3 packet contains RRCConnectionReconfiguration, THE Parser SHALL identify it as RRCConnectionReconfiguration
4. WHEN processing GSMTAPv3 messages, THE Parser SHALL maintain the same message identification accuracy as non-encapsulated messages
5. WHEN GSMTAPv3 messages are detected, THE Parser SHALL check both the protocol layer and top-level keys for message elements

### Requirement 6: Support Multiple Layer Key Formats

**User Story:** As a developer, I want the parser to handle different tshark JSON layer key formats, so that the system works with various tshark versions and configurations.

#### Acceptance Criteria

1. WHEN tshark outputs layer keys with hyphens (e.g., 'lte-rrc', 'nr-rrc'), THE Parser SHALL process them correctly
2. WHEN tshark outputs layer keys with underscores (e.g., 'lte_rrc', 'nr_rrc'), THE Parser SHALL process them correctly
3. WHEN processing a JSON packet, THE Parser SHALL check for both hyphen and underscore variants of layer keys
4. WHEN both 'lte-rrc' and 'lte_rrc' keys exist in the same packet, THE Parser SHALL prioritize the hyphen variant

### Requirement 7: Parse NAS 5GS Messages

**User Story:** As a telecom engineer, I want all NAS 5GS (5G) messages to be parsed correctly, so that I can analyze 5G mobility and session management procedures.

#### Acceptance Criteria

1. WHEN a packet contains a 5GMM message, THE Parser SHALL identify the message type using the message type hex code
2. WHEN a packet contains a 5GSM message, THE Parser SHALL identify the message type using the message type hex code
3. WHEN a NAS 5GS message is security protected, THE Parser SHALL identify it as "Security Protected NAS"
4. WHEN a NAS 5GS message is plain (not encrypted), THE Parser SHALL extract the actual message name
5. WHEN a UL/DL NAS Transport message contains nested NAS messages, THE Parser SHALL extract the nested message name
6. WHEN a NAS 5GS message type is unknown, THE Parser SHALL display the hex code
7. WHEN determining message direction, THE Parser SHALL use the 3GPP TS 24.501 specification mapping

### Requirement 8: Parse NAS EPS Messages

**User Story:** As a telecom engineer, I want all NAS EPS (4G) messages to be parsed correctly, so that I can analyze LTE mobility and session management procedures.

#### Acceptance Criteria

1. WHEN a packet contains an EMM message, THE Parser SHALL identify the message type using the message type hex code
2. WHEN a packet contains an ESM message, THE Parser SHALL identify the message type using the message type hex code
3. WHEN a NAS EPS message is security protected, THE Parser SHALL check for decrypted message content
4. WHEN a NAS EPS message cannot be decrypted, THE Parser SHALL identify it as "Security Protected NAS"
5. WHEN a NAS EPS message type is unknown, THE Parser SHALL display the hex code
6. WHEN determining message direction, THE Parser SHALL use the 3GPP TS 24.301 specification mapping

### Requirement 9: Correctly Identify Message Direction

**User Story:** As a telecom engineer, I want each message to be labeled with the correct direction (UL/DL), so that I can understand the message flow in the call diagram.

#### Acceptance Criteria

1. WHEN parsing a DL_DCCH message, THE Parser SHALL set Message_Direction to 'DL'
2. WHEN parsing a UL_DCCH message, THE Parser SHALL set Message_Direction to 'UL'
3. WHEN parsing a DL_CCCH message, THE Parser SHALL set Message_Direction to 'DL'
4. WHEN parsing a UL_CCCH message, THE Parser SHALL set Message_Direction to 'UL'
5. WHEN parsing a BCCH or PCCH message, THE Parser SHALL set Message_Direction to 'DL'
6. WHEN parsing GSMTAPv3 encapsulated messages, THE Parser SHALL determine direction based on message type patterns
7. WHEN parsing NAS messages, THE Parser SHALL use the direction from the message type mapping

### Requirement 10: Determine Source and Destination Nodes

**User Story:** As a telecom engineer, I want the system to automatically determine the source and destination nodes for each message, so that the call flow diagram accurately represents the network architecture.

#### Acceptance Criteria

1. WHEN a message is LTE RRC DL, THE System SHALL set source to 'eNB' and destination to 'UE'
2. WHEN a message is LTE RRC UL, THE System SHALL set source to 'UE' and destination to 'eNB'
3. WHEN a message is NR RRC DL, THE System SHALL set source to 'gNB' and destination to 'UE'
4. WHEN a message is NR RRC UL, THE System SHALL set source to 'UE' and destination to 'gNB'
5. WHEN a message is NAS EPS DL, THE System SHALL set source to 'MME' and destination to 'UE'
6. WHEN a message is NAS EPS UL, THE System SHALL set source to 'UE' and destination to 'MME'
7. WHEN a message is NAS 5GS DL, THE System SHALL set source to 'AMF' and destination to 'UE'
8. WHEN a message is NAS 5GS UL, THE System SHALL set source to 'UE' and destination to 'AMF'

### Requirement 11: Display Interactive Call Flow Diagram

**User Story:** As a telecom engineer, I want to see an interactive call flow diagram with messages displayed as arrows between nodes, so that I can visualize the protocol sequence.

#### Acceptance Criteria

1. WHEN messages are parsed, THE UI SHALL display a call flow diagram with 5 node columns (UE, eNB, MME, gNB, AMF)
2. WHEN displaying a message, THE UI SHALL draw an arrow from source to destination node
3. WHEN a message is UL, THE UI SHALL display the arrow in blue color
4. WHEN a message is DL, THE UI SHALL display the arrow in red color
5. WHEN displaying a message, THE UI SHALL show the message name as a label above the arrow
6. WHEN a message has nested messages, THE UI SHALL display the nested message in smaller font within parentheses
7. WHEN displaying timestamps, THE UI SHALL format them as HH:MM:SS.mmm (3-digit milliseconds)
8. WHEN the diagram is rendered, THE UI SHALL display vertical dashed lines for each node column
9. WHEN messages are loaded, THE UI SHALL display the total message count

### Requirement 12: Show Message Details Panel

**User Story:** As a telecom engineer, I want to click on a message to see its detailed Information Elements, so that I can inspect the protocol parameters.

#### Acceptance Criteria

1. WHEN a user clicks on a message arrow, THE UI SHALL open a details panel on the right side
2. WHEN the details panel opens, THE UI SHALL display basic information (frame number, timestamp, protocol, direction, nodes)
3. WHEN the details panel opens, THE UI SHALL display the full IE tree structure in JSON format
4. WHEN displaying the IE tree, THE UI SHALL use syntax highlighting (keys, strings, numbers, booleans)
5. WHEN displaying the IE tree, THE UI SHALL show only the relevant protocol layer data (not all layers)
6. WHEN a user presses Escape key, THE UI SHALL close the details panel
7. WHEN a user clicks the close button, THE UI SHALL close the details panel
8. WHEN tshark splits strings into indexed objects, THE UI SHALL reconstruct them as readable strings

### Requirement 13: Handle Nested Message Extraction

**User Story:** As a developer, I want the parser to extract nested messages from complex protocol structures, so that all relevant information is displayed to the user.

#### Acceptance Criteria

1. WHEN an RRC message contains a dedicatedNAS_Message_tree, THE Parser SHALL extract the nested NAS message
2. WHEN a NAS 5GS message contains a Payload container, THE Parser SHALL extract nested NAS messages from it
3. WHEN an LTE RRC message contains nr_SecondaryCellGroupConfig_r15_tree, THE Parser SHALL extract nested NR RRC messages
4. WHEN extracting nested messages, THE Parser SHALL search recursively up to a reasonable depth limit
5. WHEN nested message extraction fails, THE Parser SHALL continue processing without crashing
6. WHEN a nested message is found, THE Parser SHALL format the display as "Parent Message (Nested Message)"

### Requirement 14: Handle Message Tree Structures

**User Story:** As a developer, I want the parser to navigate complex nested JSON structures, so that messages can be extracted regardless of tshark output variations.

#### Acceptance Criteria

1. WHEN an RRC message contains a message_tree element, THE Parser SHALL navigate into it to find the actual message type
2. WHEN an RRC message contains a c1_tree element, THE Parser SHALL navigate into it to find the actual message type
3. WHEN an RRC message contains a criticalExtensions_tree element, THE Parser SHALL navigate into it to find message details
4. WHEN navigating nested structures, THE Parser SHALL search recursively up to a reasonable depth limit
5. WHEN a message type is found at any valid nesting level, THE Parser SHALL extract it correctly

### Requirement 15: Generate Debug Information

**User Story:** As a developer, I want the system to generate debug files during processing, so that I can troubleshoot parsing issues.

#### Acceptance Criteria

1. WHEN tshark conversion completes, THE System SHALL save a debug file with protocol information
2. WHEN call flow parsing completes, THE System SHALL save a parse debug JSON file
3. WHEN the parse debug file is created, THE System SHALL include total packet count and parsed flow count
4. WHEN the parse debug file is created, THE System SHALL include sample debug information for the first 5 packets
5. WHEN errors occur, THE System SHALL save error details to debug files
6. WHEN debug files are created, THE System SHALL use the naming pattern: {base_name}_debug.txt or {base_name}_parse_debug.json

### Requirement 16: Maintain Backward Compatibility

**User Story:** As a developer, I want the parsing improvements to maintain backward compatibility, so that existing functionality continues to work correctly.

#### Acceptance Criteria

1. WHEN parsing NAS-only messages (without RRC), THE Parser SHALL continue to extract them correctly
2. WHEN parsing messages that were previously working, THE Parser SHALL produce the same or better results
3. WHEN the improved parser encounters unknown message types, THE Parser SHALL return 'Unknown' without crashing
4. WHEN processing malformed JSON, THE Parser SHALL handle errors gracefully and continue processing remaining packets
5. WHEN a message cannot be parsed, THE Parser SHALL skip it and continue with the next message

### Requirement 17: Format Timestamps Consistently

**User Story:** As a telecom engineer, I want timestamps to be displayed in a consistent, readable format, so that I can easily correlate messages with external logs.

#### Acceptance Criteria

1. WHEN parsing frame timestamps, THE System SHALL extract the time portion from the full timestamp string
2. WHEN formatting timestamps, THE System SHALL use the format HH:MM:SS.mmm (3-digit milliseconds)
3. WHEN timestamp parsing fails, THE System SHALL return the original timestamp string
4. WHEN displaying timestamps in the UI, THE System SHALL align them consistently in the time column

### Requirement 18: Handle Large Files Efficiently

**User Story:** As a telecom engineer, I want to process large log files without timeouts or crashes, so that I can analyze long test sessions.

#### Acceptance Criteria

1. WHEN processing files larger than 100MB, THE System SHALL display a warning about processing time
2. WHEN running scat conversion, THE System SHALL use no timeout (timeout=None)
3. WHEN running tshark conversion, THE System SHALL use no timeout (timeout=None)
4. WHEN processing large files, THE System SHALL display progress information to the user
5. WHEN file size exceeds 2GB, THE System SHALL reject the upload before processing begins

### Requirement 19: Validate Dependencies on Startup

**User Story:** As a user, I want the system to check for required external tools on startup, so that I receive clear error messages if dependencies are missing.

#### Acceptance Criteria

1. WHEN a file is uploaded, THE System SHALL check if scat is installed
2. WHEN a file is uploaded, THE System SHALL check if tshark is installed
3. WHEN scat is not found, THE System SHALL return an error message "scat이 설치되지 않았습니다"
4. WHEN tshark is not found, THE System SHALL return an error message "tshark가 설치되지 않았습니다"
5. WHEN dependency checks timeout, THE System SHALL treat it as a missing dependency

### Requirement 20: Extract SystemInformation SIB Types

**User Story:** As a telecom engineer, I want SystemInformation messages to show which SIB types they contain, so that I can identify broadcast information blocks.

#### Acceptance Criteria

1. WHEN a SystemInformation message is parsed, THE Parser SHALL search for SIB type elements
2. WHEN SIB elements are found, THE Parser SHALL extract the SIB numbers (e.g., SIB2, SIB3)
3. WHEN multiple SIBs are present, THE Parser SHALL list them in numerical order
4. WHEN SIBs are found, THE Parser SHALL format the message name as "SystemInformation (SIB2 SIB3)"
5. WHEN no SIBs are found, THE Parser SHALL display only "SystemInformation"
6. WHEN searching for SIBs, THE Parser SHALL search recursively up to depth 10
