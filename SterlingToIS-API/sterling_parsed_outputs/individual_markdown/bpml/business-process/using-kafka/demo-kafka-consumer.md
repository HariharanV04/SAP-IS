# Demo_Kafka_Consumer

**Type**: sterling.process
**File**: demo-kafka-consumer.bpml

## Description

Sterling B2B Business Process: Demo_Kafka_Consumer

## Operations

### 1. Kafka Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Action`: get
  - `BootStrapServers`: localhost:29092
  - `KafkaClientAdapter`: KafkaClientAdapter
  - `SecurityAction`: PLAINTEXT
  - `GroupId`: demo-sfg-consumer-0001
  - `.`: {'from': 'PrimaryDocument'}

### 2. Kafka Client Consumer Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Topic`: sb2b-kfk-inbound

### 3. Kafka Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Action`: get

