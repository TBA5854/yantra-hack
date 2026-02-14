import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'package:go_router/go_router.dart';
import '../../../features/risk/risk_provider.dart';
import '../../../data/models/risk_snapshot.dart';
import '../../../data/models/stress_factor.dart';

/// Command Center - Instant system state overview
/// Clean, minimalist design - NO glassmorphism
class CommandCenterPage extends ConsumerWidget {
  const CommandCenterPage({super.key});

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
                // Page title
                _buildPageTitle(),
                const SizedBox(height: 32),

                // Zone A: Risk Dominance (60/40 split)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Left: Risk Score
                    Expanded(
                      flex: 6,
                      child: _buildRiskScoreCard(
                        riskState.riskScore,
                        riskState.riskLevel,
                      ),
                    ),
                    const SizedBox(width: 24),

                    // Right: System State
                    Expanded(
                      flex: 4,
                      child: _buildSystemStateCard(
                        context,
                        riskState.tcs,
                        riskState.windowState,
                        riskState.finalityWeight,
                        riskState.completeness,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                // Zone B: Risk Timeline
                _buildRiskTimeline(riskState.history),

                const SizedBox(height: 24),

                // Zone C: Stress Snapshot (4 cards)
                _buildStressSnapshot(context, riskState.stressBreakdown),
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
          'COMMAND CENTER',
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
      ],
    );
  }

  Widget _buildRiskScoreCard(int score, String level) {
    Color scoreColor = const Color(0xFF00FF88); // Green
    if (score > 50) scoreColor = const Color(0xFFFFCC00); // Yellow
    if (score > 80) scoreColor = const Color(0xFFFF3333); // Red

    return Container(
      height: 280,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F0F),
        border: Border.all(
          color: const Color(0xFF1A1A1A),
          width: 1,
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Large score number
          Text(
            score.toString(),
            style: GoogleFonts.robotoMono(
              color: scoreColor,
              fontSize: 96,
              fontWeight: FontWeight.bold,
              height: 1,
            ),
          ),
          const SizedBox(height: 16),

          // Risk level
          Text(
            level.toUpperCase(),
            style: GoogleFonts.robotoMono(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.w600,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 8),

          // Subtitle
          Text(
            'CONTINUOUS RISK SCORE',
            style: GoogleFonts.robotoMono(
              color: Colors.grey[700],
              fontSize: 10,
              letterSpacing: 1,
            ),
          ),

          const SizedBox(height: 24),

          // Progress bar
          _buildProgressBar(score / 100, scoreColor),
        ],
      ),
    );
  }

  Widget _buildProgressBar(double value, Color color) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '0',
              style: GoogleFonts.robotoMono(
                color: Colors.grey[700],
                fontSize: 10,
              ),
            ),
            Text(
              '50',
              style: GoogleFonts.robotoMono(
                color: Colors.grey[700],
                fontSize: 10,
              ),
            ),
            Text(
              '100',
              style: GoogleFonts.robotoMono(
                color: Colors.grey[700],
                fontSize: 10,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          height: 4,
          decoration: BoxDecoration(
            color: const Color(0xFF1A1A1A),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: value,
            child: Container(
              color: color,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSystemStateCard(
    BuildContext context,
    double tcs,
    String windowState,
    double finality,
    double completeness,
  ) {
    return InkWell(
      onTap: () => context.go('/confidence'),
      child: Container(
        height: 280,
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
            Text(
              'SYSTEM STATE',
              style: GoogleFonts.robotoMono(
                color: Colors.grey[600],
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1,
              ),
            ),
            const SizedBox(height: 24),

            // TCS
            _buildMetric(
              'CONFIDENCE',
              '${(tcs * 100).toInt()}%',
              const Color(0xFF00E5FF),
            ),
            const SizedBox(height: 20),

            // Window State
            _buildMetric(
              'WINDOW',
              windowState,
              Colors.white,
            ),
            const SizedBox(height: 20),

            // Finality
            _buildMetric(
              'FINALITY',
              'T-${(finality * 3).ceil()}',
              const Color(0xFFAA88FF),
            ),
            const SizedBox(height: 20),

            // Data Completeness
            _buildMetric(
              'DATA',
              '${(completeness * 100).toInt()}%',
              const Color(0xFF00FF88),
            ),

            const Spacer(),

            // Tap hint
            Row(
              children: [
                Icon(
                  Icons.arrow_forward,
                  color: Colors.grey[800],
                  size: 12,
                ),
                const SizedBox(width: 8),
                Text(
                  'View details',
                  style: GoogleFonts.robotoMono(
                    color: Colors.grey[800],
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetric(String label, String value, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: GoogleFonts.robotoMono(
            color: Colors.grey[700],
            fontSize: 11,
          ),
        ),
        Text(
          value,
          style: GoogleFonts.robotoMono(
            color: color,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildRiskTimeline(List<RiskSnapshot> history) {
    final sortedHistory = List<RiskSnapshot>.from(history)
      ..sort((a, b) => a.timestamp.compareTo(b.timestamp));

    return Container(
      height: 320,
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
          Text(
            'RISK TIMELINE',
            style: GoogleFonts.robotoMono(
              color: Colors.grey[600],
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 24),
          Expanded(
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
                titlesData: FlTitlesData(
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: sortedHistory.length > 10
                          ? (sortedHistory.length / 6).floorToDouble()
                          : 1,
                      getTitlesWidget: (value, meta) {
                        int index = value.toInt();
                        if (index >= 0 && index < sortedHistory.length) {
                          return Padding(
                            padding: const EdgeInsets.only(top: 8.0),
                            child: Text(
                              DateFormat('HH:mm')
                                  .format(sortedHistory[index].timestamp),
                              style: GoogleFonts.robotoMono(
                                color: Colors.grey[700],
                                fontSize: 9,
                              ),
                            ),
                          );
                        }
                        return const Text('');
                      },
                    ),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: 25,
                      reservedSize: 35,
                      getTitlesWidget: (value, meta) => Text(
                        value.toInt().toString(),
                        style: GoogleFonts.robotoMono(
                          color: Colors.grey[700],
                          fontSize: 9,
                        ),
                      ),
                    ),
                  ),
                  topTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  rightTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                ),
                borderData: FlBorderData(show: false),
                minX: 0,
                maxX: (sortedHistory.length - 1).toDouble(),
                minY: 0,
                maxY: 100,
                lineBarsData: [
                  LineChartBarData(
                    spots: sortedHistory.asMap().entries.map((e) {
                      return FlSpot(
                        e.key.toDouble(),
                        e.value.riskScore.toDouble(),
                      );
                    }).toList(),
                    isCurved: true,
                    color: const Color(0xFF00E5FF),
                    barWidth: 2,
                    isStrokeCapRound: true,
                    dotData: FlDotData(
                      show: true,
                      getDotPainter: (spot, percent, barData, index) {
                        bool hasEvent = sortedHistory[index].event != null;
                        return FlDotCirclePainter(
                          radius: hasEvent ? 4 : 2,
                          color: hasEvent
                              ? const Color(0xFFFFCC00)
                              : const Color(0xFF00E5FF),
                          strokeWidth: 0,
                        );
                      },
                    ),
                    belowBarData: BarAreaData(
                      show: true,
                      color: const Color(0xFF00E5FF).withOpacity(0.1),
                    ),
                  ),
                ],
                lineTouchData: LineTouchData(
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipColor: (spot) => const Color(0xFF1A1A1A),
                    getTooltipItems: (touchedSpots) {
                      return touchedSpots.map((spot) {
                        final index = spot.x.toInt();
                        final data = sortedHistory[index];
                        return LineTooltipItem(
                          '${DateFormat('HH:mm:ss').format(data.timestamp)}\n'
                          'Risk: ${data.riskScore}\n'
                          'Conf: ${(data.confidence * 100).toInt()}%',
                          GoogleFonts.robotoMono(
                            color: Colors.white,
                            fontSize: 10,
                          ),
                        );
                      }).toList();
                    },
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStressSnapshot(
    BuildContext context,
    Map<String, StressFactor> stressBreakdown,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'STRESS FACTORS',
          style: GoogleFonts.robotoMono(
            color: Colors.grey[600],
            fontSize: 10,
            fontWeight: FontWeight.bold,
            letterSpacing: 1,
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: stressBreakdown.entries.map((entry) {
            return Expanded(
              child: Padding(
                padding: const EdgeInsets.only(right: 16.0),
                child: _buildStressCard(context, entry.key, entry.value),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildStressCard(
    BuildContext context,
    String title,
    StressFactor factor,
  ) {
    Color color = const Color(0xFF00FF88);
    if (factor.value > 50) color = const Color(0xFFFFCC00);
    if (factor.value > 80) color = const Color(0xFFFF3333);

    return InkWell(
      onTap: () => context.go('/stress'),
      child: Container(
        height: 140,
        padding: const EdgeInsets.all(16),
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
            Text(
              title.toUpperCase(),
              style: GoogleFonts.robotoMono(
                color: Colors.grey[700],
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Spacer(),
            Text(
              factor.value.toStringAsFixed(1),
              style: GoogleFonts.robotoMono(
                color: color,
                fontSize: 32,
                fontWeight: FontWeight.bold,
                height: 1,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${(factor.contributionPercent * 100).toInt()}%',
                  style: GoogleFonts.robotoMono(
                    color: Colors.grey[700],
                    fontSize: 10,
                  ),
                ),
                _buildMiniSparkline(factor.history, color),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMiniSparkline(List<double> history, Color color) {
    if (history.isEmpty) return const SizedBox(width: 40, height: 20);
    return SizedBox(
      width: 40,
      height: 20,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(show: false),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: history
                  .asMap()
                  .entries
                  .map((e) => FlSpot(e.key.toDouble(), e.value))
                  .toList(),
              isCurved: true,
              color: color,
              barWidth: 1,
              dotData: FlDotData(show: false),
              belowBarData: BarAreaData(show: false),
            ),
          ],
        ),
      ),
    );
  }
}
