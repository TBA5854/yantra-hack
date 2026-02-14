// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chain_finality_data.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ChainFinalityDataImpl _$$ChainFinalityDataImplFromJson(
  Map<String, dynamic> json,
) => _$ChainFinalityDataImpl(
  chain: json['chain'] as String,
  confirmations: (json['confirmations'] as num).toInt(),
  tier: json['tier'] as String,
  finalized: json['finalized'] as bool,
  lastReorg: DateTime.parse(json['lastReorg'] as String),
  confidence: (json['confidence'] as num).toDouble(),
);

Map<String, dynamic> _$$ChainFinalityDataImplToJson(
  _$ChainFinalityDataImpl instance,
) => <String, dynamic>{
  'chain': instance.chain,
  'confirmations': instance.confirmations,
  'tier': instance.tier,
  'finalized': instance.finalized,
  'lastReorg': instance.lastReorg.toIso8601String(),
  'confidence': instance.confidence,
};
