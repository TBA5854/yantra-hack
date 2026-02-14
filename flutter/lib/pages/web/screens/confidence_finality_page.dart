import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../../../features/risk/risk_provider.dart';
import '../../../data/models/chain_finality_data.dart';

/// Confidence & Finality - Meta-confidence quantification
/// Clean, minimalist design - NO glassmorphism
class ConfidenceFinalityPage extends ConsumerWidget {
  const ConfidenceFinalityPage({super.key});

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

                // TCS Overview
                _buildTCSOverview(
                  riskState.tcs,
                  riskState.finalityWeight,
                  riskState.crossChainConfidence,
                  riskState.completeness,
                  riskState.stalenessPenalty,
                ),

                const SizedBox(height: 32),

                // Chain Finality Table
                _buildChainFinalityTable(riskState.chainFinalityList),

                const SizedBox(height: 32),

                // Window State Machine
                _buildWindowStateMachine(riskState.windowState),
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
          'CONFIDENCE & FINALITY',
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
          'Meta-awareness of risk assessment quality',
          style: GoogleFonts.robotoMono(
            color: Colors.grey[700],
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildTCSOverview(
    double tcs,
    double finalityWeight,
    double crossChainConfidence,
    double completeness,
    double stalenessPenalty,
  ) {
    Color tcsColor = const Color(0xFFFF3333);
    String tcsStatus = 'POOR';
    if (tcs > 0.6) {
      tcsColor = const Color(0xFFFFCC00);
      tcsStatus = 'PROBABLE';
    }
    if (tcs > 0.9) {
      tcsColor = const Color(0xFF00FF88);
      tcsStatus = 'FINAL';
    }

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
          Text(
            'TEMPORAL CONFIDENCE SCORE (TCS)',
            style: GoogleFonts.robotoMono(
              color: Colors.grey[600],
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 24),

          // Large TCS display
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${(tcs * 100).toStringAsFixed(1)}%',
                style: GoogleFonts.robotoMono(
                  color: tcsColor,
                  fontSize: 64,
                  fontWeight: FontWeight.bold,
                  height: 1,
                ),
              ),
              const SizedBox(width: 16),
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(
                  tcsStatus,
                  style: GoogleFonts.robotoMono(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 2,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 32),

          // Progress bar
          _buildTCSProgressBar(tcs, tcsColor),

          const SizedBox(height: 32),

          // Breakdown
          Text(
            'CONFIDENCE BREAKDOWN',
            style: GoogleFonts.robotoMono(
              color: Colors.grey[600],
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 16),

          Row(
            children: [
              Expanded(
                child: _buildBreakdownCard(
                  'FINALITY',
                  finalityWeight,
                  const Color(0xFF00E5FF),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildBreakdownCard(
                  'X-CHAIN',
                  crossChainConfidence,
                  const Color(0xFFAA88FF),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildBreakdownCard(
                  'COMPLETE',
                  completeness,
                  const Color(0xFF00FF88),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildBreakdownCard(
                  'STALENESS',
                  stalenessPenalty,
                  const Color(0xFFFF3333),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTCSProgressBar(double value, Color color) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '0%',
              style: GoogleFonts.robotoMono(
                color: Colors.grey[700],
                fontSize: 10,
              ),
            ),
            Text(
              '60%',
              style: GoogleFonts.robotoMono(
                color: Colors.grey[700],
                fontSize: 10,
              ),
            ),
            Text(
              '90%',
              style: GoogleFonts.robotoMono(
                color: Colors.grey[700],
                fontSize: 10,
              ),
            ),
            Text(
              '100%',
              style: GoogleFonts.robotoMono(
                color: Colors.grey[700],
                fontSize: 10,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          height: 8,
          decoration: BoxDecoration(
            color: const Color(0xFF1A1A1A),
          ),
          child: Stack(
            children: [
              // Threshold markers
              Positioned(
                left: 0,
                right: 0,
                child: Row(
                  children: [
                    Expanded(flex: 60, child: Container()),
                    Container(width: 1, color: Colors.grey[800]),
                    Expanded(flex: 30, child: Container()),
                    Container(width: 1, color: Colors.grey[800]),
                    Expanded(flex: 10, child: Container()),
                  ],
                ),
              ),
              // Progress
              FractionallySizedBox(
                alignment: Alignment.centerLeft,
                widthFactor: value,
                child: Container(
                  color: color,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildBreakdownCard(String label, double value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0A0A),
        border: Border.all(
          color: const Color(0xFF1A1A1A),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: GoogleFonts.robotoMono(
              color: Colors.grey[700],
              fontSize: 9,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '${(value * 100).toStringAsFixed(0)}%',
            style: GoogleFonts.robotoMono(
              color: color,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            height: 2,
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
      ),
    );
  }

  Widget _buildChainFinalityTable(List<ChainFinalityData> chainFinalityList) {
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
          Text(
            'CHAIN FINALITY STATUS',
            style: GoogleFonts.robotoMono(
              color: Colors.grey[600],
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 16),

          // Table
          Table(
            border: TableBorder(
              horizontalInside: BorderSide(
                color: const Color(0xFF1A1A1A),
                width: 1,
              ),
            ),
            columnWidths: const {
              0: FlexColumnWidth(2),
              1: FlexColumnWidth(2),
              2: FlexColumnWidth(1.5),
              3: FlexColumnWidth(1.5),
              4: FlexColumnWidth(2),
              5: FlexColumnWidth(2),
            },
            children: [
              // Header
              TableRow(
                children: [
                  _buildTableHeader('CHAIN'),
                  _buildTableHeader('CONFIRMATIONS'),
                  _buildTableHeader('TIER'),
                  _buildTableHeader('FINALIZED'),
                  _buildTableHeader('LAST REORG'),
                  _buildTableHeader('CONFIDENCE'),
                ],
              ),

              // Data rows
              ...chainFinalityList.map((data) {
                return TableRow(
                  children: [
                    _buildTableCell(data.chain, isChainName: true),
                    _buildTableCell(data.confirmations.toString()),
                    _buildTierCell(data.tier),
                    _buildFinalizedCell(data.finalized),
                    _buildTableCell(
                      DateFormat('HH:mm:ss').format(data.lastReorg),
                    ),
                    _buildConfidenceCell(data.confidence),
                  ],
                );
              }).toList(),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTableHeader(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      child: Text(
        text,
        style: GoogleFonts.robotoMono(
          color: Colors.grey[700],
          fontSize: 9,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildTableCell(String text, {bool isChainName = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      child: Text(
        text,
        style: GoogleFonts.robotoMono(
          color: isChainName ? Colors.white : Colors.grey[500],
          fontSize: 11,
          fontWeight: isChainName ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }

  Widget _buildTierCell(String tier) {
    Color color = Colors.grey;
    if (tier == 'Tier 1') color = const Color(0xFF00E5FF);
    if (tier == 'Tier 2') color = const Color(0xFFAA88FF);
    if (tier == 'Tier 3') color = const Color(0xFF00FF88);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(
          border: Border.all(
            color: color.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Text(
          tier,
          style: GoogleFonts.robotoMono(
            color: color,
            fontSize: 9,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  Widget _buildFinalizedCell(bool finalized) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: finalized
                  ? const Color(0xFF00FF88)
                  : const Color(0xFFFFCC00),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            finalized ? 'YES' : 'PENDING',
            style: GoogleFonts.robotoMono(
              color: finalized
                  ? const Color(0xFF00FF88)
                  : const Color(0xFFFFCC00),
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConfidenceCell(double confidence) {
    Color color = const Color(0xFFFF3333);
    if (confidence > 0.8) color = const Color(0xFFFFCC00);
    if (confidence > 0.95) color = const Color(0xFF00FF88);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${(confidence * 100).toStringAsFixed(1)}%',
            style: GoogleFonts.robotoMono(
              color: Colors.white,
              fontSize: 11,
            ),
          ),
          const SizedBox(height: 4),
          Container(
            height: 2,
            width: 60,
            decoration: BoxDecoration(
              color: const Color(0xFF1A1A1A),
            ),
            child: FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: confidence,
              child: Container(
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWindowStateMachine(String currentState) {
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
          Text(
            'WINDOW STATE MACHINE',
            style: GoogleFonts.robotoMono(
              color: Colors.grey[600],
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 24),

          // State progression
          Row(
            children: [
              _buildStateBox('OPEN', currentState == 'OPEN'),
              _buildArrow(),
              _buildStateBox('PROVISIONAL', currentState == 'PROVISIONAL'),
              _buildArrow(),
              _buildStateBox('FINAL', currentState == 'FINAL'),
            ],
          ),

          const SizedBox(height: 24),

          // Explanation
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0A0A0A),
              border: Border.all(
                color: const Color(0xFF1A1A1A),
                width: 1,
              ),
            ),
            child: Text(
              _getStateExplanation(currentState),
              style: GoogleFonts.robotoMono(
                color: Colors.grey[500],
                fontSize: 11,
                height: 1.6,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStateBox(String state, bool isActive) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFF1A1A1A) : const Color(0xFF0A0A0A),
          border: Border.all(
            color: isActive
                ? const Color(0xFF00E5FF)
                : const Color(0xFF1A1A1A),
            width: isActive ? 2 : 1,
          ),
        ),
        child: Center(
          child: Text(
            state,
            style: GoogleFonts.robotoMono(
              color: isActive ? const Color(0xFF00E5FF) : Colors.grey[700],
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildArrow() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Icon(
        Icons.arrow_forward,
        color: Colors.grey[800],
        size: 16,
      ),
    );
  }

  String _getStateExplanation(String state) {
    switch (state) {
      case 'OPEN':
        return 'Window is actively collecting events. Data is real-time but not yet finalized.';
      case 'PROVISIONAL':
        return 'Window closed but contains unfinalized events. Awaiting blockchain finality.';
      case 'FINAL':
        return 'All events finalized. Safe for immutable attestation on-chain.';
      default:
        return 'Unknown state';
    }
  }
}
