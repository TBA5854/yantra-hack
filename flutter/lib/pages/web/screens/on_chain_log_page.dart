import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../../../features/risk/risk_provider.dart';

/// On-Chain Alerts - Immutable transparency layer
/// Clean, minimalist design - NO glassmorphism
class OnChainLogPage extends ConsumerStatefulWidget {
  const OnChainLogPage({super.key});

  @override
  ConsumerState<OnChainLogPage> createState() => _OnChainLogPageState();
}

class _OnChainLogPageState extends ConsumerState<OnChainLogPage> {
  String _filter = 'all'; // all, red, finalized

  @override
  Widget build(BuildContext context) {
    final riskStateAsync = ref.watch(riskNotifierProvider);

    return riskStateAsync.when(
      data: (riskState) {
        // Mock alert data (in production, this would come from blockchain)
        final alerts = _generateMockAlerts();
        final filteredAlerts = _applyFilter(alerts);

        return Container(
          color: const Color(0xFF0A0A0A),
          padding: const EdgeInsets.all(32.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildPageTitle(),
              const SizedBox(height: 32),

              // Filters
              _buildFilters(),
              const SizedBox(height: 24),

              // Alert table
              Expanded(
                child: _buildAlertTable(filteredAlerts),
              ),
            ],
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
          'ON-CHAIN ALERTS',
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
          'Immutable risk alerts logged on-chain',
          style: GoogleFonts.robotoMono(
            color: Colors.grey[700],
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildFilters() {
    return Row(
      children: [
        _buildFilterButton('All Alerts', 'all'),
        const SizedBox(width: 12),
        _buildFilterButton('Red Only', 'red'),
        const SizedBox(width: 12),
        _buildFilterButton('Finalized', 'finalized'),
      ],
    );
  }

  Widget _buildFilterButton(String label, String value) {
    final isActive = _filter == value;

    return InkWell(
      onTap: () => setState(() => _filter = value),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFF1A1A1A) : const Color(0xFF0F0F0F),
          border: Border.all(
            color: isActive
                ? const Color(0xFF00E5FF)
                : const Color(0xFF1A1A1A),
            width: 1,
          ),
        ),
        child: Text(
          label.toUpperCase(),
          style: GoogleFonts.robotoMono(
            color: isActive ? const Color(0xFF00E5FF) : Colors.grey[600],
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  Widget _buildAlertTable(List<Map<String, dynamic>> alerts) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F0F),
        border: Border.all(
          color: const Color(0xFF1A1A1A),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFF0A0A0A),
              border: Border(
                bottom: BorderSide(
                  color: const Color(0xFF1A1A1A),
                  width: 1,
                ),
              ),
            ),
            child: Row(
              children: [
                Expanded(flex: 2, child: _buildTableHeader('STABLECOIN')),
                Expanded(flex: 1, child: _buildTableHeader('RISK')),
                Expanded(flex: 1, child: _buildTableHeader('CONFIDENCE')),
                Expanded(flex: 2, child: _buildTableHeader('TIMESTAMP')),
                Expanded(flex: 3, child: _buildTableHeader('TX HASH')),
                Expanded(flex: 1, child: _buildTableHeader('TIER')),
              ],
            ),
          ),

          // Rows
          Expanded(
            child: alerts.isEmpty
                ? Center(
                    child: Text(
                      'No alerts match filter',
                      style: GoogleFonts.robotoMono(
                        color: Colors.grey[700],
                        fontSize: 11,
                      ),
                    ),
                  )
                : ListView.builder(
                    itemCount: alerts.length,
                    itemBuilder: (context, index) {
                      return _buildAlertRow(alerts[index]);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildTableHeader(String text) {
    return Text(
      text,
      style: GoogleFonts.robotoMono(
        color: Colors.grey[700],
        fontSize: 9,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Widget _buildAlertRow(Map<String, dynamic> alert) {
    Color riskColor = const Color(0xFF00FF88);
    if (alert['risk'] > 50) riskColor = const Color(0xFFFFCC00);
    if (alert['risk'] > 80) riskColor = const Color(0xFFFF3333);

    return InkWell(
      onTap: () => _showAlertDetail(alert),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: const Color(0xFF1A1A1A),
              width: 1,
            ),
          ),
        ),
        child: Row(
          children: [
            // Stablecoin
            Expanded(
              flex: 2,
              child: Text(
                alert['coin'],
                style: GoogleFonts.robotoMono(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            // Risk
            Expanded(
              flex: 1,
              child: Text(
                alert['risk'].toString(),
                style: GoogleFonts.robotoMono(
                  color: riskColor,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            // Confidence
            Expanded(
              flex: 1,
              child: Text(
                '${(alert['confidence'] * 100).toInt()}%',
                style: GoogleFonts.robotoMono(
                  color: Colors.grey[500],
                  fontSize: 11,
                ),
              ),
            ),

            // Timestamp
            Expanded(
              flex: 2,
              child: Text(
                DateFormat('yyyy-MM-dd HH:mm:ss').format(alert['timestamp']),
                style: GoogleFonts.robotoMono(
                  color: Colors.grey[500],
                  fontSize: 11,
                ),
              ),
            ),

            // TX Hash
            Expanded(
              flex: 3,
              child: Row(
                children: [
                  Text(
                    alert['txHash'],
                    style: GoogleFonts.robotoMono(
                      color: const Color(0xFF00E5FF),
                      fontSize: 11,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Icon(
                    Icons.open_in_new,
                    color: Colors.grey[700],
                    size: 12,
                  ),
                ],
              ),
            ),

            // Tier
            Expanded(
              flex: 1,
              child: _buildTierBadge(alert['tier']),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTierBadge(String tier) {
    Color color = Colors.grey;
    if (tier == 'T1') color = const Color(0xFF00E5FF);
    if (tier == 'T2') color = const Color(0xFFAA88FF);
    if (tier == 'T3') color = const Color(0xFF00FF88);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Center(
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

  void _showAlertDetail(Map<String, dynamic> alert) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: const Color(0xFF0F0F0F),
        child: Container(
          width: 600,
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'ALERT DETAILS',
                style: GoogleFonts.robotoMono(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                ),
              ),
              const SizedBox(height: 24),

              _buildDetailRow('Stablecoin', alert['coin']),
              _buildDetailRow('Risk Score', alert['risk'].toString()),
              _buildDetailRow(
                'Confidence',
                '${(alert['confidence'] * 100).toInt()}%',
              ),
              _buildDetailRow(
                'Timestamp',
                DateFormat('yyyy-MM-dd HH:mm:ss').format(alert['timestamp']),
              ),
              _buildDetailRow('Transaction Hash', alert['txHash']),
              _buildDetailRow('Finality Tier', alert['tier']),

              const SizedBox(height: 24),

              Container(
                padding: const EdgeInsets.all(16),
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
                      'STRESS SNAPSHOT',
                      style: GoogleFonts.robotoMono(
                        color: Colors.grey[600],
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Peg: ${alert['pegStress']}\n'
                      'Liquidity: ${alert['liquidityStress']}\n'
                      'Supply: ${alert['supplyStress']}\n'
                      'Market: ${alert['marketStress']}',
                      style: GoogleFonts.robotoMono(
                        color: Colors.grey[500],
                        fontSize: 11,
                        height: 1.6,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text(
                    'CLOSE',
                    style: GoogleFonts.robotoMono(
                      color: const Color(0xFF00E5FF),
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          SizedBox(
            width: 150,
            child: Text(
              label.toUpperCase(),
              style: GoogleFonts.robotoMono(
                color: Colors.grey[700],
                fontSize: 10,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: GoogleFonts.robotoMono(
                color: Colors.white,
                fontSize: 11,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Mock data generation
  List<Map<String, dynamic>> _generateMockAlerts() {
    final now = DateTime.now();
    return [
      {
        'coin': 'USDC',
        'risk': 85,
        'confidence': 0.95,
        'timestamp': now.subtract(const Duration(hours: 2)),
        'txHash': '0x7a3f...9e2d',
        'tier': 'T3',
        'pegStress': 78.5,
        'liquidityStress': 65.2,
        'supplyStress': 42.1,
        'marketStress': 55.8,
      },
      {
        'coin': 'USDT',
        'risk': 45,
        'confidence': 0.88,
        'timestamp': now.subtract(const Duration(hours: 5)),
        'txHash': '0x2b1c...4f7a',
        'tier': 'T2',
        'pegStress': 35.2,
        'liquidityStress': 48.9,
        'supplyStress': 52.3,
        'marketStress': 41.7,
      },
      {
        'coin': 'DAI',
        'risk': 22,
        'confidence': 0.92,
        'timestamp': now.subtract(const Duration(hours: 8)),
        'txHash': '0x9d5e...1a8c',
        'tier': 'T3',
        'pegStress': 18.4,
        'liquidityStress': 25.6,
        'supplyStress': 21.9,
        'marketStress': 28.3,
      },
      {
        'coin': 'USDC',
        'risk': 92,
        'confidence': 0.78,
        'timestamp': now.subtract(const Duration(days: 1)),
        'txHash': '0x4c8b...6d3e',
        'tier': 'T2',
        'pegStress': 88.7,
        'liquidityStress': 82.4,
        'supplyStress': 75.1,
        'marketStress': 91.2,
      },
    ];
  }

  List<Map<String, dynamic>> _applyFilter(List<Map<String, dynamic>> alerts) {
    switch (_filter) {
      case 'red':
        return alerts.where((a) => a['risk'] > 80).toList();
      case 'finalized':
        return alerts.where((a) => a['tier'] == 'T3').toList();
      default:
        return alerts;
    }
  }
}
