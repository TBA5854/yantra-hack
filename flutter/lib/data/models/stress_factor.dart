import 'package:freezed_annotation/freezed_annotation.dart';

part 'stress_factor.freezed.dart';
part 'stress_factor.g.dart';

@freezed
class StressFactor with _$StressFactor {
  const factory StressFactor({
    required double value,
    required String trend, // 'up', 'down', 'stable'
    required double rollingMean,
    required double contributionPercent,
    required List<double> history, // Micro-history for sparklines
    required String description, // Mechanism Insight
  }) = _StressFactor;

  factory StressFactor.fromJson(Map<String, dynamic> json) =>
      _$StressFactorFromJson(json);
}
