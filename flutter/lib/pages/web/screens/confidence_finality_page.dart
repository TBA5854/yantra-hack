import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../../../../features/risk/risk_provider.dart';
import '../../../../data/models/chain_finality_data.dart';

class ConfidenceFinalityPage extends ConsumerWidget {
  const ConfidenceFinalityPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final riskStateAsync = ref.watch(riskNotifierProvider);

    return Scaffold(
      backgroundColor: Colors.black, // Dark tech theme
      body: riskStateAsync.when(
        data: (riskState) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(),
                const SizedBox(height: 32),
                _buildConfidenceOverview(
                  context,
                  riskState.tcs,
                  riskState.finalityWeight,
                  riskState.crossChainConfidence,
                  riskState.completeness,
                  riskState.stalenessPenalty,
                ),
                const SizedBox(height: 48),
                _buildChainFinalityTable(context, riskState.chainFinalityList),
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
          'CONFIDENCE & FINALITY',
          style: GoogleFonts.robotoMono(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.5,
          ),
        ),
        const SizedBox(height: 8),
        Container(width: 60, height: 2, color: Colors.cyanAccent),
      ],
    );
  }

  Widget _buildConfidenceOverview(
    BuildContext context,
    double tcs,
    double finalityWeight,
    double crossChainConfidence,
    double completeness,
    double stalenessPenalty,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'TOTAL CONFIDENCE SCORE (TCS)',
          style: GoogleFonts.robotoMono(
            color: Colors.grey[400],
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        _buildTCSGauge(tcs),
        const SizedBox(height: 32),
        Text(
          'CONFIDENCE BREAKDOWN',
          style: GoogleFonts.robotoMono(
            color: Colors.grey[400],
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        _buildBreakdownVisualization(
          finalityWeight,
          crossChainConfidence,
          completeness,
          stalenessPenalty,
        ),
      ],
    );
  }

  Widget _buildTCSGauge(double tcs) {
    // Determine color based on TCS
    Color gaugeColor = Colors.redAccent;
    if (tcs > 0.7) gaugeColor = Colors.orangeAccent;
    if (tcs > 0.9) gaugeColor = Colors.greenAccent;

    return Container(
      height: 60,
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Stack(
        children: [
          // Background ticks
          Row(
            children: List.generate(20, (index) {
              return Expanded(
                child: Container(
                  margin: const EdgeInsets.symmetric(horizontal: 1),
                  color: Colors.black.withOpacity(0.3),
                ),
              );
            }),
          ),
          // Progress Bar
          FractionallySizedBox(
            widthFactor: tcs,
            child: Container(
              decoration: BoxDecoration(
                color: gaugeColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Align(
                alignment: Alignment.centerRight,
                child: Container(width: 2, color: gaugeColor),
              ),
            ),
          ),
          // Filled area gradient
          FractionallySizedBox(
            widthFactor: tcs,
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    gaugeColor.withOpacity(0.1),
                    gaugeColor.withOpacity(0.6),
                  ],
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                ),
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
          // Text Value
          Center(
            child: Text(
              '${(tcs * 100).toStringAsFixed(1)}%',
              style: GoogleFonts.robotoMono(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBreakdownVisualization(
    double finalityWeight,
    double crossChainConfidence,
    double completeness,
    double stalenessPenalty,
  ) {
    // Normalize values roughly to show contribution.
    // In a real scenario, we'd know exactly how TCS is calculated.
    // Here we'll just stack them to visualize relative weights.

    // Using a row of cards for clarity
    return Row(
      children: [
        Expanded(
          child: _buildBreakdownCard(
            'FINALITY',
            finalityWeight,
            Colors.blueAccent,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildBreakdownCard(
            'X-CHAIN',
            crossChainConfidence,
            Colors.purpleAccent,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildBreakdownCard(
            'COMPLETE',
            completeness,
            Colors.tealAccent,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildBreakdownCard(
            'STALENESS',
            stalenessPenalty,
            Colors.redAccent,
            isPenalty: true,
          ),
        ),
      ],
    );
  }

  Widget _buildBreakdownCard(
    String label,
    double value,
    Color color, {
    bool isPenalty = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: GoogleFonts.robotoMono(
              color: Colors.grey[500],
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(
                isPenalty ? Icons.arrow_downward : Icons.arrow_upward,
                color: color,
                size: 14,
              ),
              const SizedBox(width: 4),
              Text(
                '${(value * 100).toStringAsFixed(0)}%',
                style: GoogleFonts.robotoMono(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          LinearProgressIndicator(
            value: value,
            backgroundColor: Colors.grey[800],
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 2,
          ),
        ],
      ),
    );
  }

  Widget _buildChainFinalityTable(
    BuildContext context,
    List<ChainFinalityData> chainFinalityList,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'CHAIN FINALITY STATUS',
          style: GoogleFonts.robotoMono(
            color: Colors.grey[400],
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[800]!),
            borderRadius: BorderRadius.circular(4),
          ),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              headingRowColor: MaterialStateProperty.all(Colors.grey[900]),
              columnSpacing: 32,
              columns: const [
                DataColumn(
                  label: Text(
                    'CHAIN',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ),
                DataColumn(
                  label: Text(
                    'CONFIRMATIONS',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ),
                DataColumn(
                  label: Text(
                    'TIER',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ),
                DataColumn(
                  label: Text(
                    'FINALIZED',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ),
                DataColumn(
                  label: Text(
                    'LAST REORG',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ),
                DataColumn(
                  label: Text(
                    'CONFIDENCE',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ),
              ],
              rows: chainFinalityList.map((data) {
                return DataRow(
                  cells: [
                    DataCell(
                      Text(
                        data.chain,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    DataCell(
                      Text(
                        data.confirmations.toString(),
                        style: GoogleFonts.robotoMono(color: Colors.white),
                      ),
                    ),
                    DataCell(_buildTierBadge(data.tier)),
                    DataCell(_buildFinalizedStatus(data.finalized)),
                    DataCell(
                      Text(
                        DateFormat('HH:mm:ss').format(data.lastReorg),
                        style: GoogleFonts.robotoMono(color: Colors.grey[400]),
                      ),
                    ),
                    DataCell(_buildConfidenceCell(data.confidence)),
                  ],
                );
              }).toList(),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTierBadge(String tier) {
    Color color = Colors.grey;
    if (tier == 'Tier 1') color = Colors.cyanAccent;
    if (tier == 'Tier 2') color = Colors.blueAccent;
    if (tier == 'Tier 3') color = Colors.purpleAccent;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        border: Border.all(color: color.withOpacity(0.5)),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        tier,
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildFinalizedStatus(bool finalized) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          finalized ? Icons.check_circle_outline : Icons.error_outline,
          color: finalized ? Colors.greenAccent : Colors.orangeAccent,
          size: 16,
        ),
        const SizedBox(width: 4),
        Text(
          finalized ? 'YES' : 'PENDING',
          style: TextStyle(
            color: finalized ? Colors.greenAccent : Colors.orangeAccent,
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildConfidenceCell(double confidence) {
    Color color = Colors.redAccent;
    if (confidence > 0.8) color = Colors.orangeAccent;
    if (confidence > 0.95) color = Colors.greenAccent;

    return Container(
      width: 100,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${(confidence * 100).toStringAsFixed(1)}%',
            style: GoogleFonts.robotoMono(color: Colors.white, fontSize: 12),
          ),
          SizedBox(height: 2),
          LinearProgressIndicator(
            value: confidence,
            backgroundColor: Colors.grey[800],
            valueColor: AlwaysStoppedAnimation(color),
            minHeight: 2,
          ),
        ],
      ),
    );
  }
}
