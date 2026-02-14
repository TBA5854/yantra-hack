// ignore_for_file: unused_import
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../../features/risk/risk_provider.dart';
import '../../../../data/models/stress_factor.dart';

class StressBreakdownPage extends ConsumerWidget {
  const StressBreakdownPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final riskStateAsync = ref.watch(riskNotifierProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      body: riskStateAsync.when(
        data: (riskState) {
          final stressBreakdown = riskState.stressBreakdown;
          // Split factors
          final pegFactors = stressBreakdown.entries
              .where((e) => e.key == 'peg')
              .toList();
          final otherFactors = stressBreakdown.entries
              .where((e) => e.key != 'peg')
              .toList();

          return SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(),
                const SizedBox(height: 32),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Left Column: Peg Stress Module (Primary)
                    Expanded(
                      flex: 1,
                      child: Column(
                        children: pegFactors
                            .map(
                              (e) => _buildDetailedModule(
                                e.key,
                                e.value,
                                isPrimary: true,
                              ),
                            )
                            .toList(),
                      ),
                    ),
                    const SizedBox(width: 24),
                    // Right Column: Other Modules
                    Expanded(
                      flex: 1,
                      child: Column(
                        children: otherFactors
                            .map((e) => _buildDetailedModule(e.key, e.value))
                            .toList(),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(
          child: Text('Error: $err', style: const TextStyle(color: Colors.red)),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'STRESS ANALYSIS',
          style: GoogleFonts.robotoMono(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.5,
          ),
        ),
        const SizedBox(height: 8),
        Container(width: 60, height: 2, color: Colors.redAccent),
      ],
    );
  }

  Widget _buildDetailedModule(
    String title,
    StressFactor factor, {
    bool isPrimary = false,
  }) {
    Color color = Colors.greenAccent;
    if (factor.value > 50) color = Colors.orangeAccent;
    if (factor.value > 80) color = Colors.redAccent;

    return Container(
      margin: const EdgeInsets.only(bottom: 24),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: isPrimary ? color.withOpacity(0.5) : Colors.grey[800]!,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title.toUpperCase(),
                style: GoogleFonts.robotoMono(
                  color: Colors.white,
                  fontSize: isPrimary ? 20 : 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  factor.trend.toUpperCase(),
                  style: GoogleFonts.robotoMono(
                    color: color,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                factor.value.toStringAsFixed(1),
                style: GoogleFonts.robotoMono(
                  color: color,
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'ROLLING: ${factor.rollingMean.toStringAsFixed(1)}',
                    style: GoogleFonts.robotoMono(
                      color: Colors.grey[500],
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    'CONTRIB: ${(factor.contributionPercent * 100).toInt()}%',
                    style: GoogleFonts.robotoMono(
                      color: Colors.grey[500],
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 8),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          // Trend Chart
          _buildTrendChart(factor.history, color),
          const SizedBox(height: 24),
          // Mechanism Insight
          Text(
            'MECHANISM INSIGHT',
            style: GoogleFonts.robotoMono(
              color: Colors.grey[400],
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            factor.description,
            style: GoogleFonts.robotoMono(
              color: Colors.grey[300],
              fontSize: 12,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrendChart(List<double> history, Color color) {
    if (history.isEmpty) {
      return Container(
        height: 100,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: Colors.black26,
          borderRadius: BorderRadius.circular(4),
        ),
        child: Text(
          'No historical data',
          style: GoogleFonts.robotoMono(color: Colors.grey),
        ),
      );
    }
    return SizedBox(
      height: 150,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: true, drawVerticalLine: false),
          titlesData: FlTitlesData(show: false),
          borderData: FlBorderData(show: false),
          minY: 0,
          maxY: 100,
          lineBarsData: [
            LineChartBarData(
              spots: history
                  .asMap()
                  .entries
                  .map((e) => FlSpot(e.key.toDouble(), e.value))
                  .toList(),
              isCurved: true,
              color: color,
              barWidth: 2,
              isStrokeCapRound: true,
              dotData: FlDotData(
                show: true,
                getDotPainter: (spot, percent, barData, index) =>
                    FlDotCirclePainter(radius: 3, color: color, strokeWidth: 0),
              ),
              belowBarData: BarAreaData(
                show: true,
                color: color.withOpacity(0.1),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
