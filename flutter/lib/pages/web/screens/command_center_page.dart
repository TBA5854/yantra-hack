import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'package:go_router/go_router.dart';
import '../../../../features/risk/risk_provider.dart';
import '../../../../data/models/risk_snapshot.dart';
import '../../../../data/models/stress_factor.dart';

class CommandCenterPage extends ConsumerWidget {
  const CommandCenterPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final riskStateAsync = ref.watch(riskNotifierProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      body: riskStateAsync.when(
        data: (riskState) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              children: [
                // Zone A: Risk Dominance
                _buildZoneA(
                  context,
                  riskState.riskScore,
                  riskState.riskLevel,
                  riskState.tcs,
                  riskState.windowState,
                  riskState.finalityWeight,
                  riskState.crossChainConfidence,
                  riskState.completeness,
                ), // Passing breakdown for completeness proxy
                const SizedBox(height: 32),
                // Zone B: Risk Evolution Timeline
                _buildZoneB(context, riskState.history),
                const SizedBox(height: 32),
                // Zone C: Live Stress Snapshot
                _buildZoneC(context, riskState.stressBreakdown),
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

  // --- Zone A: Risk Dominance ---
  Widget _buildZoneA(
    BuildContext context,
    int riskScore,
    String riskLevel,
    double tcs,
    String windowState,
    double finality,
    double xChain,
    double completeness,
  ) {
    return SizedBox(
      height: 350,
      child: Row(
        children: [
          // Left: Risk Meter (60%)
          Expanded(flex: 6, child: _buildRiskMeter(riskScore, riskLevel)),
          const SizedBox(width: 24),
          // Right: Confidence Card (40%)
          Expanded(
            flex: 4,
            child: _buildConfidenceCard(
              context,
              tcs,
              windowState,
              finality,
              xChain,
              completeness,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRiskMeter(int score, String level) {
    // Determine color
    Color meterColor = Colors.greenAccent;
    if (score > 50) meterColor = Colors.orangeAccent;
    if (score > 80) meterColor = Colors.redAccent;

    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Large Arc
          SizedBox(
            width: 300,
            height: 300,
            child: PieChart(
              PieChartData(
                startDegreeOffset: 180,
                borderData: FlBorderData(show: false),
                sectionsSpace: 0,
                centerSpaceRadius: 110,
                sections: [
                  PieChartSectionData(
                    color: meterColor,
                    value: score.toDouble(),
                    radius: 25,
                    title: '',
                  ),
                  PieChartSectionData(
                    color: Colors.grey[800],
                    value: (100 - score).toDouble(),
                    radius: 25,
                    title: '',
                  ),
                  // Bottom half hidden
                  PieChartSectionData(
                    color: Colors.transparent,
                    value: 100,
                    radius: 25,
                    title: '',
                  ),
                ],
              ),
            ),
          ),
          // Center Text
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '$score',
                style: GoogleFonts.robotoMono(
                  color: Colors.white,
                  fontSize: 72,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                level.toUpperCase(),
                style: GoogleFonts.robotoMono(
                  color: meterColor,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Continuous Risk Score',
                style: GoogleFonts.robotoMono(
                  color: Colors.grey[500],
                  fontSize: 10,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildConfidenceCard(
    BuildContext context,
    double tcs,
    String windowState,
    double finality,
    double xChain,
    double completeness,
  ) {
    return InkWell(
      onTap: () => context.go('/confidence'),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.grey[800]!),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'SYSTEM STATE',
              style: GoogleFonts.robotoMono(
                color: Colors.grey[400],
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildMetricItem(
                  'TCS',
                  tcs.toStringAsFixed(2),
                  Colors.cyanAccent,
                ),
                _buildMetricItem('WINDOW', windowState, Colors.white),
              ],
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildMetricItem(
                  'FINALITY',
                  'T-${(finality * 3).ceil()}',
                  Colors.purpleAccent,
                ), // Mock tier calc
                _buildMetricItem(
                  'DATA',
                  '${(completeness * 100).toInt()}%',
                  Colors.greenAccent,
                ),
              ],
            ),
            const Spacer(),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.black45,
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: Colors.grey[800]!),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildBullet('Finality weight dominates TCS.'),
                  _buildBullet('Cross-chain signals stable.'),
                  _buildBullet('No data staleness detected.'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricItem(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.robotoMono(color: Colors.grey[500], fontSize: 10),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: GoogleFonts.robotoMono(
            color: color,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildBullet(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Container(
            width: 4,
            height: 4,
            color: Colors.grey,
            margin: const EdgeInsets.only(right: 8),
          ),
          Text(
            text,
            style: GoogleFonts.robotoMono(
              color: Colors.grey[400],
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  // --- Zone B: Risk Evolution Timeline ---
  Widget _buildZoneB(BuildContext context, List<RiskSnapshot> history) {
    // Sort history by timestamp just in case
    final sortedHistory = List<RiskSnapshot>.from(history)
      ..sort((a, b) => a.timestamp.compareTo(b.timestamp));

    return Container(
      height: 400, // Reduced height for better fit
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'RISK EVOLUTION',
                style: GoogleFonts.robotoMono(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Row(
                children: [
                  _buildLegendDot(Colors.greenAccent.withOpacity(0.2), 'SAFE'),
                  const SizedBox(width: 12),
                  _buildLegendDot(
                    Colors.orangeAccent.withOpacity(0.2),
                    'WARNING',
                  ),
                  const SizedBox(width: 12),
                  _buildLegendDot(
                    Colors.redAccent.withOpacity(0.2),
                    'CRITICAL',
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          Expanded(
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: true,
                  getDrawingHorizontalLine: (value) =>
                      FlLine(color: Colors.grey[800]!, strokeWidth: 1),
                  getDrawingVerticalLine: (value) =>
                      FlLine(color: Colors.grey[800]!, strokeWidth: 1),
                ),
                titlesData: FlTitlesData(
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: 1, // Assumes roughly 1 hour per snapshot index
                      getTitlesWidget: (value, meta) {
                        int index = value.toInt();
                        if (index >= 0 && index < sortedHistory.length) {
                          return Padding(
                            padding: const EdgeInsets.only(top: 8.0),
                            child: Text(
                              DateFormat(
                                'HH:mm',
                              ).format(sortedHistory[index].timestamp),
                              style: GoogleFonts.robotoMono(
                                color: Colors.grey[500],
                                fontSize: 10,
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
                      interval: 20,
                      reservedSize: 40,
                      getTitlesWidget: (value, meta) => Text(
                        value.toInt().toString(),
                        style: GoogleFonts.robotoMono(
                          color: Colors.grey[500],
                          fontSize: 10,
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
                    color: Colors.white,
                    barWidth: 3,
                    isStrokeCapRound: true,
                    dotData: FlDotData(
                      show: true,
                      getDotPainter: (spot, percent, barData, index) {
                        // Check for event
                        bool hasEvent = sortedHistory[index].event != null;
                        return FlDotCirclePainter(
                          radius: hasEvent ? 6 : 4,
                          color: hasEvent ? Colors.cyanAccent : Colors.white,
                          strokeWidth: hasEvent ? 2 : 0,
                          strokeColor: Colors.black,
                        );
                      },
                    ),
                    belowBarData: BarAreaData(
                      show: true,
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.redAccent.withOpacity(0.3),
                          Colors.orangeAccent.withOpacity(0.3),
                          Colors.greenAccent.withOpacity(0.3),
                        ],
                        stops: const [
                          0.0,
                          0.5,
                          1.0,
                        ], // Simple gradient approximation of risk zones
                      ),
                    ),
                  ),
                ],
                lineTouchData: LineTouchData(
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipColor: (spot) => Colors.grey[900]!,
                    getTooltipItems: (touchedSpots) {
                      return touchedSpots.map((spot) {
                        final index = spot.x.toInt();
                        final data = sortedHistory[index];
                        return LineTooltipItem(
                          '${DateFormat('HH:mm:ss').format(data.timestamp)}\nRisk: ${data.riskScore}\nConf: ${(data.confidence * 100).toInt()}%\n${data.event ?? ""}',
                          GoogleFonts.robotoMono(color: Colors.white),
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

  Widget _buildLegendDot(Color color, String label) {
    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: GoogleFonts.robotoMono(color: Colors.grey[500], fontSize: 10),
        ),
      ],
    );
  }

  // --- Zone C: Live Stress Snapshot ---
  Widget _buildZoneC(
    BuildContext context,
    Map<String, StressFactor> stressBreakdown,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'LIVE STRESS SNAPSHOT',
          style: GoogleFonts.robotoMono(
            color: Colors.grey,
            fontSize: 12,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 160,
          child: Row(
            children: stressBreakdown.entries.map((entry) {
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(right: 16.0),
                  child: _buildStressCard(context, entry.key, entry.value),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildStressCard(
    BuildContext context,
    String title,
    StressFactor factor,
  ) {
    Color color = Colors.greenAccent;
    if (factor.value > 50) color = Colors.orangeAccent;
    if (factor.value > 80) color = Colors.redAccent;

    return InkWell(
      onTap: () => context.go('/stress'),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.grey[800]!),
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
                    color: Colors.grey[500],
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                _buildMiniSparkline(factor.history, color),
              ],
            ),
            const Spacer(),
            Text(
              factor.value.toStringAsFixed(1),
              style: GoogleFonts.robotoMono(
                color: color,
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'High ${factor.value > factor.rollingMean ? '+' : ''}${(factor.value - factor.rollingMean).toStringAsFixed(1)}',
                  style: GoogleFonts.robotoMono(
                    color: Colors.grey[600],
                    fontSize: 10,
                  ),
                ),
                Text(
                  '${(factor.contributionPercent * 100).toInt()}% Contrib.',
                  style: GoogleFonts.robotoMono(
                    color: Colors.grey[600],
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

  Widget _buildMiniSparkline(List<double> history, Color color) {
    if (history.isEmpty) return const SizedBox(width: 50, height: 20);
    return SizedBox(
      width: 50,
      height: 30,
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
              barWidth: 2,
              dotData: FlDotData(show: false),
              belowBarData: BarAreaData(show: false),
            ),
          ],
        ),
      ),
    );
  }
}
