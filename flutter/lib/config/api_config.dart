/// Configuration for API endpoints
class ApiConfig {
  // Base URL for ML Risk API
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
  
  // WebSocket URL
  static String get wsUrl => baseUrl.replaceFirst('http', 'ws');
  
  // Default coin
  static const String defaultCoin = 'USDC';
  
  // Default chain
  static const String defaultChain = 'ethereum';
  
  // Refresh interval for polling (when WebSocket not available)
  static const Duration refreshInterval = Duration(seconds: 5);
  
  // API timeout
  static const Duration timeout = Duration(seconds: 10);
}
