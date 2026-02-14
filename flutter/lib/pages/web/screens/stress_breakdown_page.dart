import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../features/risk/risk_provider.dart';
import '../../../data/models/stress_factor.dart';

/// Stress Analysis - Deep dive into stress factors
/// Clean, minimalist design - NO glassmorphism
class StressBreakdownPage extends ConsumerWidget {
  const StressBreakdownPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final riskStateAsync = ref.watch(riskNotifierProvider);

    return riskStateAsync.when(
      data: (riskState) {
        return Container(
          color: const Color(0xFF0A0A0A),
          padding: const EdgeInsets.all(32.0),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildPageTitle(),
                const SizedBox(height: 32),

                // Grid layout: 2x2 stress modules
                _buildStressGrid(riskState.stressBreakdown),
              ],
            ),
          ),
        );
      },
      loading: () => const Center(
        child: CircularProgressIndicator(
          color: Color(0xFF00E5FF),
        ),
      ),
      error: (err, stack) => Center(
        child: Text(
          'Error: $err',
          style: const TextStyle(color: Colors.red),
        ),
      ),
    );
  }

  Widget _buildPageTitle() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'STRESS ANALYSIS',
          style: GoogleFonts.robotoMono(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: 60,
          height: 2,
          color: const Color(0xFF00E5FF),
        ),
        const SizedBox(height: 12),
        Text(
          'Structural breakdown of stabilization mechanism stress',
          style: GoogleFonts.robotoMono(
            color: Colors.grey[700],
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildStressGrid(Map<String, StressFactor> stressBreakdown) {
    final entries = stressBreakdown.entries.toList();

    return Column(
      children: [
        // Top row
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (entries.isNotEmpty)
              Expanded(
                child: _buildStressModule(entries[0].key, entries[0].value),
              ),
            if (entries.length > 1) ...[
              const SizedBox(width: 24),
              Expanded(
                child: _buildStressModule(entries[1].key, entries[1].value),
              ),
            ],
          ],
        ),
        const SizedBox(height: 24),

        // Bottom row
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (entries.length > 2)
              Expanded(
                child: _buildStressModule(entries[2].key, entries[2].value),
              ),
            if (entries.length > 3) ...[
              const SizedBox(width: 24),
              Expanded(
                child: _buildStressModule(entries[3].key, entries[3].value),
              ),
            ],
          ],
        ),
      ],
    );
  }

  Widget _buildStressModule(String title, StressFactor factor) {
    Color color = const Color(0xFF00FF88);
    if (factor.value > 50) color = const Color(0xFFFFCC00);
    if (factor.value > 80) color = const Color(0xFFFF3333);

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F0F),
        border: Border.all(
          color: const Color(0xFF1A1A1A),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title.toUpperCase(),
                style: GoogleFonts.robotoMono(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  border: Border.all(
                    color: color.withOpacity(0.3),
                    width: 1,
                  ),
                ),
                child: Text(
                  factor.trend.toUpperCase(),
                  style: GoogleFonts.robotoMono(
                    color: color,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Current value
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                factor.value.toStringAsFixed(1),
                style: GoogleFonts.robotoMono(
                  color: color,
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  height: 1,
                ),
              ),
              const SizedBox(width: 16),
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildMetricRow(
                      'ROLLING',
                      factor.rollingMean.toStringAsFixed(1),
                    ),
                    const SizedBox(height: 4),
                    _buildMetricRow(
                      'CONTRIB',
                      '${(factor.contributionPercent * 100).toInt()}%',
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Trend chart
          _buildTrendChart(factor.history, color),

          const SizedBox(height: 24),

          // Divider
          Container(
            height: 1,
            color: const Color(0xFF1A1A1A),
          ),

          const SizedBox(height: 16),

          // Mechanism insight
          Text(
            'MECHANISM INSIGHT',
            style: GoogleFonts.robotoMono(
              color: Colors.grey[700],
              fontSize: 9,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            factor.description,
            style: GoogleFonts.robotoMono(
              color: Colors.grey[500],
              fontSize: 11,
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricRow(String label, String value) {
    return Row(
      children: [
        Text(
          '$label: ',
          style: GoogleFonts.robotoMono(
            color: Colors.grey[700],
            fontSize: 10,
          ),
        ),
        Text(
          value,
          style: GoogleFonts.robotoMono(
            color: Colors.grey[500],
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildTrendChart(List<double> history, Color color) {
    if (history.isEmpty) {
      return Container(
        height: 120,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: const Color(0xFF0A0A0A),
          border: Border.all(
            color: const Color(0xFF1A1A1A),
            width: 1,
          ),
        ),
        child: Text(
          'No historical data',
          style: GoogleFonts.robotoMono(
            color: Colors.grey[800],
            fontSize: 10,
          ),
        ),
      );
    }

    return Container(
      height: 120,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0A0A),
        border: Border.all(
          color: const Color(0xFF1A1A1A),
          width: 1,
        ),
      ),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: 25,
            getDrawingHorizontalLine: (value) => FlLine(
              color: const Color(0xFF1A1A1A),
              strokeWidth: 1,
            ),
          ),
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
                    FlDotCirclePainter(
                  radius: 2,
                  color: color,
                  strokeWidth: 0,
                ),
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
