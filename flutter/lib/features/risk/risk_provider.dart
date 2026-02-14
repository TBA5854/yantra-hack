import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../data/models/risk_state.dart';
import '../../data/repositories/risk_repository.dart';

part 'risk_provider.g.dart';

@riverpod
class RiskNotifier extends _$RiskNotifier {
  @override
  FutureOr<RiskState> build() {
    final repository = ref.watch(riskRepositoryProvider);
    return repository.getRiskState();
  }
}
