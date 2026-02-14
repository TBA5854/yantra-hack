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
      stressBreakdown: (json['stressBreakdown'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, StressFactor.fromJson(e as Map<String, dynamic>)),
      ),
      history: (json['history'] as List<dynamic>)
          .map((e) => RiskSnapshot.fromJson(e as Map<String, dynamic>))
          .toList(),
      chainData: json['chainData'] as Map<String, dynamic>,
      finalityWeight: (json['finalityWeight'] as num).toDouble(),
      crossChainConfidence: (json['crossChainConfidence'] as num).toDouble(),
      completeness: (json['completeness'] as num).toDouble(),
      stalenessPenalty: (json['stalenessPenalty'] as num).toDouble(),
      chainFinalityList: (json['chainFinalityList'] as List<dynamic>)
          .map((e) => ChainFinalityData.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$RiskStateImplToJson(_$RiskStateImpl instance) =>
    <String, dynamic>{
      'riskScore': instance.riskScore,
      'riskLevel': instance.riskLevel,
      'tcs': instance.tcs,
      'windowState': instance.windowState,
      'explanations': instance.explanations,
      'stressBreakdown': instance.stressBreakdown,
      'history': instance.history,
      'chainData': instance.chainData,
      'finalityWeight': instance.finalityWeight,
      'crossChainConfidence': instance.crossChainConfidence,
      'completeness': instance.completeness,
      'stalenessPenalty': instance.stalenessPenalty,
      'chainFinalityList': instance.chainFinalityList,
    };
