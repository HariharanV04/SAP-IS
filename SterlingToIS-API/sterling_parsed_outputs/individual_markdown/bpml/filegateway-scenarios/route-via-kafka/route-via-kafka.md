# Demo_BP_RouteViaKafka

**Type**: sterling.process
**File**: route-via-kafka.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaKafka

## Operations

### 1. Kafka Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Action`: put
  - `BootStrapServers`: {'from': '//customkafka_BootStrapServers/text()'}
  - `KafkaClientAdapter`: {'from': '//customkafka_KafkaClientAdapter/text()'}
  - `SecurityAction`: {'from': '//customkafka_SecurityAction/text()'}
  - `ProducerConfig`: {'from': '//customkafka_ProducerConfig/text()'}
  - `.`: {'from': 'PrimaryDocument'}

### 2. Kafka Client Producer Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Topic`: {'from': '//customkafka_Topic/text()'}
  - `.`: {'from': 'PrimaryDocument'}

### 3. Kafka Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Action`: put

