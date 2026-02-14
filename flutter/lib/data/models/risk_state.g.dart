// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'risk_state.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$RiskStateImpl _$$RiskStateImplFromJson(Map<String, dynamic> json) =>
    _$RiskStateImpl(
      riskScore: (json['riskScore'] as num).toInt(),
      riskLevel: json['riskLevel'] as String,
      tcs: (json['tcs'] as num).toDouble(),
      windowState: json['windowState'] as String,
      explanations: (json['explanations'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      stressBreakdown: json['stressBreakdown'] as Map<String, dynamic>,
      chainData: json['chainData'] as Map<String, dynamic>,
    );

Map<String, dynamic> _$$RiskStateImplToJson(_$RiskStateImpl instance) =>
    <String, dynamic>{
      'riskScore': instance.riskScore,
      'riskLevel': instance.riskLevel,
      'tcs': instance.tcs,
      'windowState': instance.windowState,
      'explanations': instance.explanations,
      'stressBreakdown': instance.stressBreakdown,
      'chainData': instance.chainData,
    };
