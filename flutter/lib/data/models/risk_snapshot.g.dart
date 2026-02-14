// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'risk_snapshot.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$RiskSnapshotImpl _$$RiskSnapshotImplFromJson(Map<String, dynamic> json) =>
    _$RiskSnapshotImpl(
      timestamp: DateTime.parse(json['timestamp'] as String),
      riskScore: (json['riskScore'] as num).toInt(),
      confidence: (json['confidence'] as num).toDouble(),
      event: json['event'] as String?,
    );

Map<String, dynamic> _$$RiskSnapshotImplToJson(_$RiskSnapshotImpl instance) =>
    <String, dynamic>{
      'timestamp': instance.timestamp.toIso8601String(),
      'riskScore': instance.riskScore,
      'confidence': instance.confidence,
      'event': instance.event,
    };
