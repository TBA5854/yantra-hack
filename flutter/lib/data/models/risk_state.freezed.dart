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
      throw _privateConstructorUsedError; // 'Green', 'Yellow', 'Red'
  double get tcs =>
      throw _privateConstructorUsedError; // Total Confidence Score
  String get windowState =>
      throw _privateConstructorUsedError; // 'OPEN', 'PROVISIONAL', 'FINAL'
  List<String> get explanations => throw _privateConstructorUsedError;
  Map<String, dynamic> get stressBreakdown =>
      throw _privateConstructorUsedError;
  Map<String, dynamic> get chainData => throw _privateConstructorUsedError;

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
    Map<String, dynamic> stressBreakdown,
    Map<String, dynamic> chainData,
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
    Object? chainData = null,
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
                      as Map<String, dynamic>,
            chainData: null == chainData
                ? _value.chainData
                : chainData // ignore: cast_nullable_to_non_nullable
                      as Map<String, dynamic>,
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
    Map<String, dynamic> stressBreakdown,
    Map<String, dynamic> chainData,
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
    Object? chainData = null,
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
                  as Map<String, dynamic>,
        chainData: null == chainData
            ? _value._chainData
            : chainData // ignore: cast_nullable_to_non_nullable
                  as Map<String, dynamic>,
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
    required final Map<String, dynamic> stressBreakdown,
    required final Map<String, dynamic> chainData,
  }) : _explanations = explanations,
       _stressBreakdown = stressBreakdown,
       _chainData = chainData;

  factory _$RiskStateImpl.fromJson(Map<String, dynamic> json) =>
      _$$RiskStateImplFromJson(json);

  @override
  final int riskScore;
  @override
  final String riskLevel;
  // 'Green', 'Yellow', 'Red'
  @override
  final double tcs;
  // Total Confidence Score
  @override
  final String windowState;
  // 'OPEN', 'PROVISIONAL', 'FINAL'
  final List<String> _explanations;
  // 'OPEN', 'PROVISIONAL', 'FINAL'
  @override
  List<String> get explanations {
    if (_explanations is EqualUnmodifiableListView) return _explanations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_explanations);
  }

  final Map<String, dynamic> _stressBreakdown;
  @override
  Map<String, dynamic> get stressBreakdown {
    if (_stressBreakdown is EqualUnmodifiableMapView) return _stressBreakdown;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_stressBreakdown);
  }

  final Map<String, dynamic> _chainData;
  @override
  Map<String, dynamic> get chainData {
    if (_chainData is EqualUnmodifiableMapView) return _chainData;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_chainData);
  }

  @override
  String toString() {
    return 'RiskState(riskScore: $riskScore, riskLevel: $riskLevel, tcs: $tcs, windowState: $windowState, explanations: $explanations, stressBreakdown: $stressBreakdown, chainData: $chainData)';
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
            const DeepCollectionEquality().equals(
              other._chainData,
              _chainData,
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
    const DeepCollectionEquality().hash(_chainData),
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
    required final Map<String, dynamic> stressBreakdown,
    required final Map<String, dynamic> chainData,
  }) = _$RiskStateImpl;

  factory _RiskState.fromJson(Map<String, dynamic> json) =
      _$RiskStateImpl.fromJson;

  @override
  int get riskScore;
  @override
  String get riskLevel; // 'Green', 'Yellow', 'Red'
  @override
  double get tcs; // Total Confidence Score
  @override
  String get windowState; // 'OPEN', 'PROVISIONAL', 'FINAL'
  @override
  List<String> get explanations;
  @override
  Map<String, dynamic> get stressBreakdown;
  @override
  Map<String, dynamic> get chainData;

  /// Create a copy of RiskState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$RiskStateImplCopyWith<_$RiskStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
