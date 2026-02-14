// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stress_factor.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$StressFactorImpl _$$StressFactorImplFromJson(Map<String, dynamic> json) =>
    _$StressFactorImpl(
      value: (json['value'] as num).toDouble(),
      trend: json['trend'] as String,
      rollingMean: (json['rollingMean'] as num).toDouble(),
      contributionPercent: (json['contributionPercent'] as num).toDouble(),
      history: (json['history'] as List<dynamic>)
          .map((e) => (e as num).toDouble())
          .toList(),
      description: json['description'] as String,
    );

Map<String, dynamic> _$$StressFactorImplToJson(_$StressFactorImpl instance) =>
    <String, dynamic>{
      'value': instance.value,
      'trend': instance.trend,
      'rollingMean': instance.rollingMean,
      'contributionPercent': instance.contributionPercent,
      'history': instance.history,
      'description': instance.description,
    };
