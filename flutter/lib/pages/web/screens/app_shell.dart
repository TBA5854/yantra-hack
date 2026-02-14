import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';

/// Unified SPA shell with persistent sidebar and top bar
/// Clean, minimalist design - NO glassmorphism
class AppShell extends StatelessWidget {
  final Widget child;
  final String currentRoute;

  const AppShell({
    super.key,
    required this.child,
    required this.currentRoute,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A), // Pure black background
      body: Row(
        children: [
          // Left Sidebar - Fixed width
          _buildSidebar(context),
          
          // Main content area
          Expanded(
            child: Column(
              children: [
                // Top bar
                _buildTopBar(context),
                
                // Page content
                Expanded(
                  child: child,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSidebar(BuildContext context) {
    return Container(
      width: 240,
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F0F),
        border: Border(
          right: BorderSide(
            color: Colors.grey[900]!,
            width: 1,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Logo/Title
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'ATLAS',
                  style: GoogleFonts.robotoMono(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(height: 4),
                Container(
                  width: 40,
                  height: 2,
                  color: const Color(0xFF00E5FF),
                ),
                const SizedBox(height: 8),
                Text(
                  'Risk Intelligence',
                  style: GoogleFonts.robotoMono(
                    color: Colors.grey[600],
                    fontSize: 10,
                    letterSpacing: 1,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Navigation items
          _buildNavItem(
            context,
            icon: Icons.dashboard_outlined,
            label: 'Command Center',
            route: '/',
            isActive: currentRoute == '/',
          ),
          _buildNavItem(
            context,
            icon: Icons.analytics_outlined,
            label: 'Stress Analysis',
            route: '/stress',
            isActive: currentRoute == '/stress',
          ),
          _buildNavItem(
            context,
            icon: Icons.verified_outlined,
            label: 'Confidence',
            route: '/confidence',
            isActive: currentRoute == '/confidence',
          ),
          _buildNavItem(
            context,
            icon: Icons.receipt_long_outlined,
            label: 'On-Chain Alerts',
            route: '/logs',
            isActive: currentRoute == '/logs',
          ),

          const Spacer(),

          // System status indicator
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: Color(0xFF00FF88),
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'LIVE',
                      style: GoogleFonts.robotoMono(
                        color: const Color(0xFF00FF88),
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'All systems operational',
                  style: GoogleFonts.robotoMono(
                    color: Colors.grey[700],
                    fontSize: 9,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String route,
    required bool isActive,
  }) {
    return InkWell(
      onTap: () => context.go(route),
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFF1A1A1A) : Colors.transparent,
          border: Border(
            left: BorderSide(
              color: isActive ? const Color(0xFF00E5FF) : Colors.transparent,
              width: 2,
            ),
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: isActive ? const Color(0xFF00E5FF) : Colors.grey[600],
              size: 18,
            ),
            const SizedBox(width: 12),
            Text(
              label,
              style: GoogleFonts.robotoMono(
                color: isActive ? Colors.white : Colors.grey[600],
                fontSize: 12,
                fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopBar(BuildContext context) {
    return Container(
      height: 60,
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F0F),
        border: Border(
          bottom: BorderSide(
            color: Colors.grey[900]!,
            width: 1,
          ),
        ),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Row(
        children: [
          // Coin selector
          _buildSelector(
            label: 'USDC',
            icon: Icons.currency_bitcoin,
          ),
          const SizedBox(width: 16),

          // Chain selector
          _buildSelector(
            label: 'Ethereum',
            icon: Icons.link,
          ),
          const SizedBox(width: 16),

          // Mode toggle
          _buildSelector(
            label: 'Live',
            icon: Icons.play_circle_outline,
          ),

          const Spacer(),

          // Current time
          Text(
            'UTC 12:31:49',
            style: GoogleFonts.robotoMono(
              color: Colors.grey[600],
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSelector({
    required String label,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A1A),
        border: Border.all(
          color: Colors.grey[800]!,
          width: 1,
        ),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: Colors.grey[500],
            size: 14,
          ),
          const SizedBox(width: 8),
          Text(
            label,
            style: GoogleFonts.robotoMono(
              color: Colors.white,
              fontSize: 11,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(width: 8),
          Icon(
            Icons.arrow_drop_down,
            color: Colors.grey[600],
            size: 16,
          ),
        ],
      ),
    );
  }
}
