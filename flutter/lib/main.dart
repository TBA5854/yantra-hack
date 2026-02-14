import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:google_fonts/google_fonts.dart';

import 'navigation/app_router.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter();

  runApp(const ProviderScope(child: RiskApp()));
}

class RiskApp extends ConsumerWidget {
  const RiskApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(goRouterProvider);

    return MaterialApp.router(
      title: 'Risk State Visualizer',
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF1E1E1E), // Dark Charcoal
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00E5FF), // Cyan accent
          secondary: Color(0xFFFFCC00), // Amber accent
          error: Color(0xFFFF3333), // Red error
          surface: Color(0xFF2C2C2C),
          onSurface: Colors.white,
        ),
        textTheme: GoogleFonts.outfitTextTheme(
          Theme.of(context).textTheme,
        ).apply(bodyColor: Colors.white, displayColor: Colors.white),
        useMaterial3: true,
      ),
      routerConfig: router,
    );
  }
}
