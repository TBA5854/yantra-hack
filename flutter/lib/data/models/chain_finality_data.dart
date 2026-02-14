import 'package:freezed_annotation/freezed_annotation.dart';

part 'chain_finality_data.freezed.dart';
part 'chain_finality_data.g.dart';

@freezed
class ChainFinalityData with _$ChainFinalityData {
  const factory ChainFinalityData({
    required String chain,
    required int confirmations,
    required String tier, // e.g., 'Tier 1', 'Tier 2'
    required bool finalized,
    required DateTime lastReorg,
    required double confidence, // 0.0 to 1.0
  }) = _ChainFinalityData;

  factory ChainFinalityData.fromJson(Map<String, dynamic> json) =>
      _$ChainFinalityDataFromJson(json);
}
