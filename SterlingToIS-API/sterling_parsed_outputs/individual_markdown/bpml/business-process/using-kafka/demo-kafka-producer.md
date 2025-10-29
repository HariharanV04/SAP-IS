# Demo_Kafka_Producer

**Type**: sterling.process
**File**: demo-kafka-producer.bpml

## Description

Sterling B2B Business Process: Demo_Kafka_Producer

## Operations

### 1. Kafka Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Action`: put
  - `BootStrapServers`: localhost:29092
  - `KafkaClientAdapter`: KafkaClientAdapter
  - `SecurityAction`: PLAINTEXT
  - `ProducerConfig`: buffer.memory=102400;compression.type=gzip
  - `.`: {'from': 'PrimaryDocument'}

### 2. Kafka Client Producer Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Topic`: sb2b-kfk-outbound
  - `.`: {'from': 'PrimaryDocument'}

### 3. Kafka Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Action`: put

