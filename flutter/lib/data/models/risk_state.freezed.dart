// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'risk_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

RiskState _$RiskStateFromJson(Map<String, dynamic> json) {
  return _RiskState.fromJson(json);
}

/// @nodoc
mixin _$RiskState {
  int get riskScore => throw _privateConstructorUsedError;
  String get riskLevel =>
      throw _privateConstructorUsedError; // 'MINIMAL', 'LOW', 'ELEVATED', 'HIGH', 'CRITICAL'
  double get tcs =>
      throw _privateConstructorUsedError; // Total Confidence Score
  String get windowState =>
      throw _privateConstructorUsedError; // 'OPEN', 'CLOSED', 'FINAL'
  List<String> get explanations => throw _privateConstructorUsedError;
  Map<String, StressFactor> get stressBreakdown =>
      throw _privateConstructorUsedError;
  List<RiskSnapshot> get history => throw _privateConstructorUsedError;
  Map<String, dynamic> get chainData =>
      throw _privateConstructorUsedError; // TCS breakdown fields
  double get finalityWeight => throw _privateConstructorUsedError;
  double get crossChainConfidence => throw _privateConstructorUsedError;
  double get completeness => throw _privateConstructorUsedError;
  double get stalenessPenalty => throw _privateConstructorUsedError;
  List<ChainFinalityData> get chainFinalityList =>
      throw _privateConstructorUsedError; // ML-specific fields
  String get riskRating =>
      throw _privateConstructorUsedError; // 'AAA', 'AA', 'A', 'B', 'C'
  bool get mlEnabled => throw _privateConstructorUsedError;
  Map<String, dynamic>? get models =>
      throw _privateConstructorUsedError; // ISO + XGB outputs
  Map<String, dynamic>? get explainability =>
      throw _privateConstructorUsedError;

  /// Serializes this RiskState to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of RiskState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $RiskStateCopyWith<RiskState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $RiskStateCopyWith<$Res> {
  factory $RiskStateCopyWith(RiskState value, $Res Function(RiskState) then) =
      _$RiskStateCopyWithImpl<$Res, RiskState>;
  @useResult
  $Res call({
    int riskScore,
    String riskLevel,
    double tcs,
    String windowState,
    List<String> explanations,
    Map<String, StressFactor> stressBreakdown,
    List<RiskSnapshot> history,
    Map<String, dynamic> chainData,
    double finalityWeight,
    double crossChainConfidence,
    double completeness,
    double stalenessPenalty,
    List<ChainFinalityData> chainFinalityList,
    String riskRating,
    bool mlEnabled,
    Map<String, dynamic>? models,
    Map<String, dynamic>? explainability,
  });
}

/// @nodoc
class _$RiskStateCopyWithImpl<$Res, $Val extends RiskState>
    implements $RiskStateCopyWith<$Res> {
  _$RiskStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of RiskState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? riskScore = null,
    Object? riskLevel = null,
    Object? tcs = null,
    Object? windowState = null,
    Object? explanations = null,
    Object? stressBreakdown = null,
    Object? history = null,
    Object? chainData = null,
    Object? finalityWeight = null,
    Object? crossChainConfidence = null,
    Object? completeness = null,
    Object? stalenessPenalty = null,
    Object? chainFinalityList = null,
    Object? riskRating = null,
    Object? mlEnabled = null,
    Object? models = freezed,
    Object? explainability = freezed,
  }) {
    return _then(
      _value.copyWith(
            riskScore: null == riskScore
                ? _value.riskScore
                : riskScore // ignore: cast_nullable_to_non_nullable
                      as int,
            riskLevel: null == riskLevel
                ? _value.riskLevel
                : riskLevel // ignore: cast_nullable_to_non_nullable
                      as String,
            tcs: null == tcs
                ? _value.tcs
                : tcs // ignore: cast_nullable_to_non_nullable
                      as double,
            windowState: null == windowState
                ? _value.windowState
                : windowState // ignore: cast_nullable_to_non_nullable
                      as String,
            explanations: null == explanations
                ? _value.explanations
                : explanations // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            stressBreakdown: null == stressBreakdown
                ? _value.stressBreakdown
                : stressBreakdown // ignore: cast_nullable_to_non_nullable
                      as Map<String, StressFactor>,
            history: null == history
                ? _value.history
                : history // ignore: cast_nullable_to_non_nullable
                      as List<RiskSnapshot>,
            chainData: null == chainData
                ? _value.chainData
                : chainData // ignore: cast_nullable_to_non_nullable
                      as Map<String, dynamic>,
            finalityWeight: null == finalityWeight
                ? _value.finalityWeight
                : finalityWeight // ignore: cast_nullable_to_non_nullable
                      as double,
            crossChainConfidence: null == crossChainConfidence
                ? _value.crossChainConfidence
                : crossChainConfidence // ignore: cast_nullable_to_non_nullable
                      as double,
            completeness: null == completeness
                ? _value.completeness
                : completeness // ignore: cast_nullable_to_non_nullable
                      as double,
            stalenessPenalty: null == stalenessPenalty
                ? _value.stalenessPenalty
                : stalenessPenalty // ignore: cast_nullable_to_non_nullable
                      as double,
            chainFinalityList: null == chainFinalityList
                ? _value.chainFinalityList
                : chainFinalityList // ignore: cast_nullable_to_non_nullable
                      as List<ChainFinalityData>,
            riskRating: null == riskRating
                ? _value.riskRating
                : riskRating // ignore: cast_nullable_to_non_nullable
                      as String,
            mlEnabled: null == mlEnabled
                ? _value.mlEnabled
                : mlEnabled // ignore: cast_nullable_to_non_nullable
                      as bool,
            models: freezed == models
                ? _value.models
                : models // ignore: cast_nullable_to_non_nullable
                      as Map<String, dynamic>?,
            explainability: freezed == explainability
                ? _value.explainability
                : explainability // ignore: cast_nullable_to_non_nullable
                      as Map<String, dynamic>?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$RiskStateImplCopyWith<$Res>
    implements $RiskStateCopyWith<$Res> {
  factory _$$RiskStateImplCopyWith(
    _$RiskStateImpl value,
    $Res Function(_$RiskStateImpl) then,
  ) = __$$RiskStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    int riskScore,
    String riskLevel,
    double tcs,
    String windowState,
    List<String> explanations,
    Map<String, StressFactor> stressBreakdown,
    List<RiskSnapshot> history,
    Map<String, dynamic> chainData,
    double finalityWeight,
    double crossChainConfidence,
    double completeness,
    double stalenessPenalty,
    List<ChainFinalityData> chainFinalityList,
    String riskRating,
    bool mlEnabled,
    Map<String, dynamic>? models,
    Map<String, dynamic>? explainability,
  });
}

/// @nodoc
class __$$RiskStateImplCopyWithImpl<$Res>
    extends _$RiskStateCopyWithImpl<$Res, _$RiskStateImpl>
    implements _$$RiskStateImplCopyWith<$Res> {
  __$$RiskStateImplCopyWithImpl(
    _$RiskStateImpl _value,
    $Res Function(_$RiskStateImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of RiskState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? riskScore = null,
    Object? riskLevel = null,
    Object? tcs = null,
    Object? windowState = null,
    Object? explanations = null,
    Object? stressBreakdown = null,
    Object? history = null,
    Object? chainData = null,
    Object? finalityWeight = null,
    Object? crossChainConfidence = null,
    Object? completeness = null,
    Object? stalenessPenalty = null,
    Object? chainFinalityList = null,
    Object? riskRating = null,
    Object? mlEnabled = null,
    Object? models = freezed,
    Object? explainability = freezed,
  }) {
    return _then(
      _$RiskStateImpl(
        riskScore: null == riskScore
            ? _value.riskScore
            : riskScore // ignore: cast_nullable_to_non_nullable
                  as int,
        riskLevel: null == riskLevel
            ? _value.riskLevel
            : riskLevel // ignore: cast_nullable_to_non_nullable
                  as String,
        tcs: null == tcs
            ? _value.tcs
            : tcs // ignore: cast_nullable_to_non_nullable
                  as double,
        windowState: null == windowState
            ? _value.windowState
            : windowState // ignore: cast_nullable_to_non_nullable
                  as String,
        explanations: null == explanations
            ? _value._explanations
            : explanations // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        stressBreakdown: null == stressBreakdown
            ? _value._stressBreakdown
            : stressBreakdown // ignore: cast_nullable_to_non_nullable
                  as Map<String, StressFactor>,
        history: null == history
            ? _value._history
            : history // ignore: cast_nullable_to_non_nullable
                  as List<RiskSnapshot>,
        chainData: null == chainData
            ? _value._chainData
            : chainData // ignore: cast_nullable_to_non_nullable
                  as Map<String, dynamic>,
        finalityWeight: null == finalityWeight
            ? _value.finalityWeight
            : finalityWeight // ignore: cast_nullable_to_non_nullable
                  as double,
        crossChainConfidence: null == crossChainConfidence
            ? _value.crossChainConfidence
            : crossChainConfidence // ignore: cast_nullable_to_non_nullable
                  as double,
        completeness: null == completeness
            ? _value.completeness
            : completeness // ignore: cast_nullable_to_non_nullable
                  as double,
        stalenessPenalty: null == stalenessPenalty
            ? _value.stalenessPenalty
            : stalenessPenalty // ignore: cast_nullable_to_non_nullable
                  as double,
        chainFinalityList: null == chainFinalityList
            ? _value._chainFinalityList
            : chainFinalityList // ignore: cast_nullable_to_non_nullable
                  as List<ChainFinalityData>,
        riskRating: null == riskRating
            ? _value.riskRating
            : riskRating // ignore: cast_nullable_to_non_nullable
                  as String,
        mlEnabled: null == mlEnabled
            ? _value.mlEnabled
            : mlEnabled // ignore: cast_nullable_to_non_nullable
                  as bool,
        models: freezed == models
            ? _value._models
            : models // ignore: cast_nullable_to_non_nullable
                  as Map<String, dynamic>?,
        explainability: freezed == explainability
            ? _value._explainability
            : explainability // ignore: cast_nullable_to_non_nullable
                  as Map<String, dynamic>?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$RiskStateImpl implements _RiskState {
  const _$RiskStateImpl({
    required this.riskScore,
    required this.riskLevel,
    required this.tcs,
    required this.windowState,
    required final List<String> explanations,
    required final Map<String, StressFactor> stressBreakdown,
    required final List<RiskSnapshot> history,
    required final Map<String, dynamic> chainData,
    required this.finalityWeight,
    required this.crossChainConfidence,
    required this.completeness,
    required this.stalenessPenalty,
    required final List<ChainFinalityData> chainFinalityList,
    required this.riskRating,
    this.mlEnabled = false,
    final Map<String, dynamic>? models,
    final Map<String, dynamic>? explainability,
  }) : _explanations = explanations,
       _stressBreakdown = stressBreakdown,
       _history = history,
       _chainData = chainData,
       _chainFinalityList = chainFinalityList,
       _models = models,
       _explainability = explainability;

  factory _$RiskStateImpl.fromJson(Map<String, dynamic> json) =>
      _$$RiskStateImplFromJson(json);

  @override
  final int riskScore;
  @override
  final String riskLevel;
  // 'MINIMAL', 'LOW', 'ELEVATED', 'HIGH', 'CRITICAL'
  @override
  final double tcs;
  // Total Confidence Score
  @override
  final String windowState;
  // 'OPEN', 'CLOSED', 'FINAL'
  final List<String> _explanations;
  // 'OPEN', 'CLOSED', 'FINAL'
  @override
  List<String> get explanations {
    if (_explanations is EqualUnmodifiableListView) return _explanations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_explanations);
  }

  final Map<String, StressFactor> _stressBreakdown;
  @override
  Map<String, StressFactor> get stressBreakdown {
    if (_stressBreakdown is EqualUnmodifiableMapView) return _stressBreakdown;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_stressBreakdown);
  }

  final List<RiskSnapshot> _history;
  @override
  List<RiskSnapshot> get history {
    if (_history is EqualUnmodifiableListView) return _history;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_history);
  }

  final Map<String, dynamic> _chainData;
  @override
  Map<String, dynamic> get chainData {
    if (_chainData is EqualUnmodifiableMapView) return _chainData;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_chainData);
  }

  // TCS breakdown fields
  @override
  final double finalityWeight;
  @override
  final double crossChainConfidence;
  @override
  final double completeness;
  @override
  final double stalenessPenalty;
  final List<ChainFinalityData> _chainFinalityList;
  @override
  List<ChainFinalityData> get chainFinalityList {
    if (_chainFinalityList is EqualUnmodifiableListView)
      return _chainFinalityList;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_chainFinalityList);
  }

  // ML-specific fields
  @override
  final String riskRating;
  // 'AAA', 'AA', 'A', 'B', 'C'
  @override
  @JsonKey()
  final bool mlEnabled;
  final Map<String, dynamic>? _models;
  @override
  Map<String, dynamic>? get models {
    final value = _models;
    if (value == null) return null;
    if (_models is EqualUnmodifiableMapView) return _models;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  // ISO + XGB outputs
  final Map<String, dynamic>? _explainability;
  // ISO + XGB outputs
  @override
  Map<String, dynamic>? get explainability {
    final value = _explainability;
    if (value == null) return null;
    if (_explainability is EqualUnmodifiableMapView) return _explainability;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'RiskState(riskScore: $riskScore, riskLevel: $riskLevel, tcs: $tcs, windowState: $windowState, explanations: $explanations, stressBreakdown: $stressBreakdown, history: $history, chainData: $chainData, finalityWeight: $finalityWeight, crossChainConfidence: $crossChainConfidence, completeness: $completeness, stalenessPenalty: $stalenessPenalty, chainFinalityList: $chainFinalityList, riskRating: $riskRating, mlEnabled: $mlEnabled, models: $models, explainability: $explainability)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$RiskStateImpl &&
            (identical(other.riskScore, riskScore) ||
                other.riskScore == riskScore) &&
            (identical(other.riskLevel, riskLevel) ||
                other.riskLevel == riskLevel) &&
            (identical(other.tcs, tcs) || other.tcs == tcs) &&
            (identical(other.windowState, windowState) ||
                other.windowState == windowState) &&
            const DeepCollectionEquality().equals(
              other._explanations,
              _explanations,
            ) &&
            const DeepCollectionEquality().equals(
              other._stressBreakdown,
              _stressBreakdown,
            ) &&
            const DeepCollectionEquality().equals(other._history, _history) &&
            const DeepCollectionEquality().equals(
              other._chainData,
              _chainData,
            ) &&
            (identical(other.finalityWeight, finalityWeight) ||
                other.finalityWeight == finalityWeight) &&
            (identical(other.crossChainConfidence, crossChainConfidence) ||
                other.crossChainConfidence == crossChainConfidence) &&
            (identical(other.completeness, completeness) ||
                other.completeness == completeness) &&
            (identical(other.stalenessPenalty, stalenessPenalty) ||
                other.stalenessPenalty == stalenessPenalty) &&
            const DeepCollectionEquality().equals(
              other._chainFinalityList,
              _chainFinalityList,
            ) &&
            (identical(other.riskRating, riskRating) ||
                other.riskRating == riskRating) &&
            (identical(other.mlEnabled, mlEnabled) ||
                other.mlEnabled == mlEnabled) &&
            const DeepCollectionEquality().equals(other._models, _models) &&
            const DeepCollectionEquality().equals(
              other._explainability,
              _explainability,
            ));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    riskScore,
    riskLevel,
    tcs,
    windowState,
    const DeepCollectionEquality().hash(_explanations),
    const DeepCollectionEquality().hash(_stressBreakdown),
    const DeepCollectionEquality().hash(_history),
    const DeepCollectionEquality().hash(_chainData),
    finalityWeight,
    crossChainConfidence,
    completeness,
    stalenessPenalty,
    const DeepCollectionEquality().hash(_chainFinalityList),
    riskRating,
    mlEnabled,
    const DeepCollectionEquality().hash(_models),
    const DeepCollectionEquality().hash(_explainability),
  );

  /// Create a copy of RiskState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$RiskStateImplCopyWith<_$RiskStateImpl> get copyWith =>
      __$$RiskStateImplCopyWithImpl<_$RiskStateImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$RiskStateImplToJson(this);
  }
}

abstract class _RiskState implements RiskState {
  const factory _RiskState({
    required final int riskScore,
    required final String riskLevel,
    required final double tcs,
    required final String windowState,
    required final List<String> explanations,
    required final Map<String, StressFactor> stressBreakdown,
    required final List<RiskSnapshot> history,
    required final Map<String, dynamic> chainData,
    required final double finalityWeight,
    required final double crossChainConfidence,
    required final double completeness,
    required final double stalenessPenalty,
    required final List<ChainFinalityData> chainFinalityList,
    required final String riskRating,
    final bool mlEnabled,
    final Map<String, dynamic>? models,
    final Map<String, dynamic>? explainability,
  }) = _$RiskStateImpl;

  factory _RiskState.fromJson(Map<String, dynamic> json) =
      _$RiskStateImpl.fromJson;

  @override
  int get riskScore;
  @override
  String get riskLevel; // 'MINIMAL', 'LOW', 'ELEVATED', 'HIGH', 'CRITICAL'
  @override
  double get tcs; // Total Confidence Score
  @override
  String get windowState; // 'OPEN', 'CLOSED', 'FINAL'
  @override
  List<String> get explanations;
  @override
  Map<String, StressFactor> get stressBreakdown;
  @override
  List<RiskSnapshot> get history;
  @override
  Map<String, dynamic> get chainData; // TCS breakdown fields
  @override
  double get finalityWeight;
  @override
  double get crossChainConfidence;
  @override
  double get completeness;
  @override
  double get stalenessPenalty;
  @override
  List<ChainFinalityData> get chainFinalityList; // ML-specific fields
  @override
  String get riskRating; // 'AAA', 'AA', 'A', 'B', 'C'
  @override
  bool get mlEnabled;
  @override
  Map<String, dynamic>? get models; // ISO + XGB outputs
  @override
  Map<String, dynamic>? get explainability;

  /// Create a copy of RiskState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$RiskStateImplCopyWith<_$RiskStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
