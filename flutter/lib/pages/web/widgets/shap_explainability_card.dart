import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// SHAP Explainability Widget
/// Displays top contributing features from ML predictions
class ShapExplainabilityCard extends StatelessWidget {
  final Map<String, dynamic>? explainability;

  const ShapExplainabilityCard({super.key, this.explainability});

  @override
  Widget build(BuildContext context) {
    if (explainability == null) {
      return const SizedBox.shrink();
    }

    final topFeatures =
        (explainability!['top_features'] as List?)?.take(5) ?? [];

    if (topFeatures.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F0F),
        border: Border.all(color: const Color(0xFF1A1A1A), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.psychology, size: 16, color: Color(0xFF00E5FF)),
              const SizedBox(width: 12),
              Text(
                'ML FEATURE CONTRIBUTIONS (SHAP)',
                style: GoogleFonts.robotoMono(
                  color: Colors.grey[600],
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          ...topFeatures.map((feature) {
            final Map<String, dynamic> f = feature as Map<String, dynamic>;
            final featureName = f['feature'] as String? ?? 'Unknown';
            final contribution = (f['contribution'] as num?)?.toDouble() ?? 0.0;
            final explanation = f['explanation'] as String? ?? '';
            final impact = f['impact'] as String? ?? 'positive';

            final contributionPercent = (contribution.abs() * 100).clamp(
              0,
              100,
            );
            final isPositive = impact == 'positive';
            final color = isPositive
                ? const Color(0xFFFF5555)
                : const Color(0xFF00FF88);

            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Feature name
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          featureName.replaceAll('_', ' ').toUpperCase(),
                          style: GoogleFonts.robotoMono(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Text(
                        '${isPositive ? '+' : '-'}${contributionPercent.toStringAsFixed(1)}%',
                        style: GoogleFonts.robotoMono(
                          color: color,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Contribution bar
                  Container(
                    height: 4,
                    decoration: BoxDecoration(color: const Color(0xFF1A1A1A)),
                    child: FractionallySizedBox(
                      alignment: Alignment.centerLeft,
                      widthFactor: contributionPercent / 100,
                      child: Container(color: color),
                    ),
                  ),
                  const SizedBox(height: 6),

                  // Explanation
                  Text(
                    explanation,
                    style: GoogleFonts.robotoMono(
                      color: Colors.grey[700],
                      fontSize: 10,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            );
          }),

          const SizedBox(height: 8),

          // Legend
          Row(
            children: [
              Container(width: 12, height: 12, color: const Color(0xFFFF5555)),
              const SizedBox(width: 6),
              Text(
                'Increases Risk',
                style: GoogleFonts.robotoMono(
                  color: Colors.grey[800],
                  fontSize: 9,
                ),
              ),
              const SizedBox(width: 16),
              Container(width: 12, height: 12, color: const Color(0xFF00FF88)),
              const SizedBox(width: 6),
              Text(
                'Reduces Risk',
                style: GoogleFonts.robotoMono(
                  color: Colors.grey[800],
                  fontSize: 9,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
