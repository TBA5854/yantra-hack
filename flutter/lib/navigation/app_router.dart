import 'package:flutter/foundation.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../pages/web/screens/app_shell.dart';
import '../pages/web/screens/command_center_page.dart';
import '../pages/web/screens/stress_breakdown_page.dart';
import '../pages/web/screens/confidence_finality_page.dart';
import '../pages/web/screens/on_chain_log_page.dart';
import '../pages/mobile/screens/current_status_screen.dart';
import '../pages/mobile/screens/risk_timeline_screen.dart';

part 'app_router.g.dart';

@riverpod
GoRouter goRouter(GoRouterRef ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      if (kIsWeb) ...[
        ShellRoute(
          builder: (context, state, child) {
            return AppShell(
              currentRoute: state.uri.path,
              child: child,
            );
          },
          routes: [
            GoRoute(
              path: '/',
              builder: (context, state) => const CommandCenterPage(),
            ),
            GoRoute(
              path: '/stress',
              builder: (context, state) => const StressBreakdownPage(),
            ),
            GoRoute(
              path: '/confidence',
              builder: (context, state) => const ConfidenceFinalityPage(),
            ),
            GoRoute(
              path: '/logs',
              builder: (context, state) => const OnChainLogPage(),
            ),
          ],
        ),
      ] else ...[
        GoRoute(
          path: '/',
          builder: (context, state) => const CurrentStatusScreen(),
        ),
        GoRoute(
          path: '/timeline',
          builder: (context, state) => const RiskTimelineScreen(),
        ),
      ],
    ],
  );
}
