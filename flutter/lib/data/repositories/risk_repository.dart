import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/risk_state.dart';
import '../models/chain_finality_data.dart';
import '../models/stress_factor.dart';
import '../models/risk_snapshot.dart';

abstract class RiskRepository {
  Future<RiskState> getRiskState({
    String coin = 'USDC',
    String chain = 'ethereum',
  });
  Stream<RiskState> riskStateStream({
    String coin = 'USDC',
    String chain = 'ethereum',
  });
}

/// HTTP-based repository connecting to FastAPI backend
class HttpRiskRepository implements RiskRepository {
  final String baseUrl;
  final http.Client client;

  HttpRiskRepository({
    this.baseUrl = 'http://localhost:8000',
    http.Client? client,
  }) : client = client ?? http.Client();

  @override
  Future<RiskState> getRiskState({
    String coin = 'USDC',
    String chain = 'ethereum',
  }) async {
    try {
      final response = await client.get(
        Uri.parse('$baseUrl/risk/current?coin=$coin&chain=$chain'),
        headers: {'Accept': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;
        return _parseRiskState(data, coin, chain);
      } else {
        throw Exception('API error: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to fetch risk state: $e');
    }
  }

  @override
  Stream<RiskState> riskStateStream({
    String coin = 'USDC',
    String chain = 'ethereum',
  }) async* {
    // Poll every 5 seconds (TODO: replace with WebSocket)
    while (true) {
      try {
        yield await getRiskState(coin: coin, chain: chain);
      } catch (e) {
        print('Error fetching risk state: $e');
      }
      await Future.delayed(const Duration(seconds: 5));
    }
  }

  RiskState _parseRiskState(
    Map<String, dynamic> json,
    String coin,
    String chain,
  ) {
    // Parse stress breakdown from ML explainability
    final stressBreakdown = _parseStressBreakdown(json);

    // Parse chain finality list
    final chainFinalityList =
        (json['chain_finality_list'] as List?)
            ?.map(
              (c) => ChainFinalityData(
                chain: c['chain'] as String,
                confirmations: c['block_confirmations'] as int,
                tier: 'Tier ${c['finality_tier']}',
                finalized: c['is_finalized'] as bool,
                lastReorg: DateTime.now(), // TODO: get from API
                confidence: json['tcs'] as double,
              ),
            )
            .toList() ??
        [];

    return RiskState(
      riskScore: (json['risk_score'] as num).round(),
      riskLevel: json['risk_level'] as String? ?? 'ELEVATED',
      riskRating: json['risk_rating'] as String? ?? 'A',
      tcs: (json['tcs'] as num).toDouble(),
      windowState: json['window_state'] as String? ?? 'FINAL',
      mlEnabled: json['ml_enabled'] as bool? ?? true,
      models: json['models'] as Map<String, dynamic>?,
      explainability: json['explainability'] as Map<String, dynamic>?,
      explanations: _extractExplanations(json),
      stressBreakdown: stressBreakdown,
      history: [], // TODO: fetch from /risk/history endpoint
      chainData: {'coin': coin, 'chain': chain},
      finalityWeight: 0.85, // TODO: get from TCS breakdown
      crossChainConfidence: 0.92,
      completeness: 0.98,
      stalenessPenalty: 0.0,
      chainFinalityList: chainFinalityList,
    );
  }

  Map<String, StressFactor> _parseStressBreakdown(Map<String, dynamic> json) {
    final breakdown = json['stress_breakdown'] as Map<String, dynamic>?;

    if (breakdown != null) {
      return {
        'peg': StressFactor(
          value: (breakdown['peg_deviation'] as num? ?? 0).toDouble(),
          trend: 'stable',
          rollingMean: (breakdown['peg_deviation'] as num? ?? 0).toDouble(),
          contributionPercent: 0.25,
          history: const [],
          description: 'Peg deviation stress',
        ),
        'volatility': StressFactor(
          value: (breakdown['price_volatility'] as num? ?? 0).toDouble(),
          trend: 'stable',
          rollingMean: (breakdown['price_volatility'] as num? ?? 0).toDouble(),
          contributionPercent: 0.25,
          history: const [],
          description: 'Price volatility stress',
        ),
        'velocity': StressFactor(
          value: (breakdown['velocity'] as num? ?? 0).toDouble(),
          trend: 'stable',
          rollingMean: (breakdown['velocity'] as num? ?? 0).toDouble(),
          contributionPercent: 0.25,
          history: const [],
          description: 'Deviation velocity stress',
        ),
        'market': StressFactor(
          value: (breakdown['market_correlation'] as num? ?? 0).toDouble(),
          trend: 'stable',
          rollingMean: (breakdown['market_correlation'] as num? ?? 0)
              .toDouble(),
          contributionPercent: 0.25,
          history: const [],
          description: 'Market correlation stress',
        ),
      };
    }

    return {};
  }

  List<String> _extractExplanations(Map<String, dynamic> json) {
    final explainability = json['explainability'] as Map<String, dynamic>?;

    if (explainability != null) {
      final topFeatures = explainability['top_features'] as List?;
      if (topFeatures != null) {
        return topFeatures
            .take(5)
            .map((f) => f['explanation'] as String? ?? 'No explanation')
            .toList();
      }
    }

    return ['ML prediction available with SHAP explanations'];
  }
}

/// Mock repository for testing without API
class MockRiskRepository implements RiskRepository {
  @override
  Future<RiskState> getRiskState({
    String coin = 'USDC',
    String chain = 'ethereum',
  }) async {
    await Future.delayed(const Duration(milliseconds: 500));
    return _generateMockData();
  }

  @override
  Stream<RiskState> riskStateStream({
    String coin = 'USDC',
    String chain = 'ethereum',
  }) async* {
    while (true) {
      await Future.delayed(const Duration(seconds: 5));
      yield _generateMockData();
    }
  }

  RiskState _generateMockData() {
    return RiskState(
      riskScore: 74,
      riskLevel: 'HIGH',
      riskRating: 'B',
      tcs: 0.82,
      windowState: 'FINAL',
      mlEnabled: true,
      models: {
        'isolation_forest': {'anomaly_score': 0.65, 'is_anomaly': true},
        'xgboost': {'predicted_class': 2, 'class_name': 'Critical'},
      },
      explainability: {
        'top_features': [
          {
            'feature': 'peg_distance_abs',
            'contribution': 0.32,
            'explanation': 'Large peg deviation',
          },
          {
            'feature': 'volatility_6h',
            'contribution': 0.18,
            'explanation': 'High volatility',
          },
        ],
      },
      explanations: [
        'Large peg deviation increases risk',
        'High volatility indicates instability',
        'BTC correlation elevated',
      ],
      stressBreakdown: {
        'peg': const StressFactor(
          value: 85,
          trend: 'up',
          rollingMean: 82,
          contributionPercent: 0.5,
          history: [80, 81, 82, 83, 84, 85, 85, 86, 85],
          description: 'Peg deviation > 1.5% for 4 consecutive hours.',
        ),
        'volatility': const StressFactor(
          value: 60,
          trend: 'down',
          rollingMean: 65,
          contributionPercent: 0.3,
          history: [70, 68, 65, 62, 60, 58, 60],
          description: 'Price volatility elevated.',
        ),
      },
      history: [
        RiskSnapshot(
          timestamp: DateTime.now().subtract(const Duration(hours: 1)),
          riskScore: 70,
          confidence: 0.85,
        ),
      ],
      chainData: {'coin': 'USDC', 'chain': 'ethereum'},
      finalityWeight: 0.85,
      crossChainConfidence: 0.92,
      completeness: 0.98,
      stalenessPenalty: 0.0,
      chainFinalityList: [
        ChainFinalityData(
          chain: 'Ethereum',
          confirmations: 64,
          tier: 'Tier 3',
          finalized: true,
          lastReorg: DateTime.parse('2023-10-27 10:00:00'),
          confidence: 0.99,
        ),
      ],
    );
  }
}

// Providers
final riskRepositoryProvider = Provider<RiskRepository>((ref) {
  // Switch between HTTP and Mock based on environment
  const useRealApi = bool.fromEnvironment('USE_REAL_API', defaultValue: true);

  if (useRealApi) {
    return HttpRiskRepository(baseUrl: 'http://localhost:8000');
  } else {
    return MockRiskRepository();
  }
});
