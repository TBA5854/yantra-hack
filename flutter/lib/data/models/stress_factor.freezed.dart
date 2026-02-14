// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'stress_factor.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

StressFactor _$StressFactorFromJson(Map<String, dynamic> json) {
  return _StressFactor.fromJson(json);
}

/// @nodoc
mixin _$StressFactor {
  double get value => throw _privateConstructorUsedError;
  String get trend =>
      throw _privateConstructorUsedError; // 'up', 'down', 'stable'
  double get rollingMean => throw _privateConstructorUsedError;
  double get contributionPercent => throw _privateConstructorUsedError;
  List<double> get history =>
      throw _privateConstructorUsedError; // Micro-history for sparklines
  String get description => throw _privateConstructorUsedError;

  /// Serializes this StressFactor to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of StressFactor
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $StressFactorCopyWith<StressFactor> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $StressFactorCopyWith<$Res> {
  factory $StressFactorCopyWith(
    StressFactor value,
    $Res Function(StressFactor) then,
  ) = _$StressFactorCopyWithImpl<$Res, StressFactor>;
  @useResult
  $Res call({
    double value,
    String trend,
    double rollingMean,
    double contributionPercent,
    List<double> history,
    String description,
  });
}

/// @nodoc
class _$StressFactorCopyWithImpl<$Res, $Val extends StressFactor>
    implements $StressFactorCopyWith<$Res> {
  _$StressFactorCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of StressFactor
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? value = null,
    Object? trend = null,
    Object? rollingMean = null,
    Object? contributionPercent = null,
    Object? history = null,
    Object? description = null,
  }) {
    return _then(
      _value.copyWith(
            value: null == value
                ? _value.value
                : value // ignore: cast_nullable_to_non_nullable
                      as double,
            trend: null == trend
                ? _value.trend
                : trend // ignore: cast_nullable_to_non_nullable
                      as String,
            rollingMean: null == rollingMean
                ? _value.rollingMean
                : rollingMean // ignore: cast_nullable_to_non_nullable
                      as double,
            contributionPercent: null == contributionPercent
                ? _value.contributionPercent
                : contributionPercent // ignore: cast_nullable_to_non_nullable
                      as double,
            history: null == history
                ? _value.history
                : history // ignore: cast_nullable_to_non_nullable
                      as List<double>,
            description: null == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                      as String,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$StressFactorImplCopyWith<$Res>
    implements $StressFactorCopyWith<$Res> {
  factory _$$StressFactorImplCopyWith(
    _$StressFactorImpl value,
    $Res Function(_$StressFactorImpl) then,
  ) = __$$StressFactorImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    double value,
    String trend,
    double rollingMean,
    double contributionPercent,
    List<double> history,
    String description,
  });
}

/// @nodoc
class __$$StressFactorImplCopyWithImpl<$Res>
    extends _$StressFactorCopyWithImpl<$Res, _$StressFactorImpl>
    implements _$$StressFactorImplCopyWith<$Res> {
  __$$StressFactorImplCopyWithImpl(
    _$StressFactorImpl _value,
    $Res Function(_$StressFactorImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of StressFactor
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? value = null,
    Object? trend = null,
    Object? rollingMean = null,
    Object? contributionPercent = null,
    Object? history = null,
    Object? description = null,
  }) {
    return _then(
      _$StressFactorImpl(
        value: null == value
            ? _value.value
            : value // ignore: cast_nullable_to_non_nullable
                  as double,
        trend: null == trend
            ? _value.trend
            : trend // ignore: cast_nullable_to_non_nullable
                  as String,
        rollingMean: null == rollingMean
            ? _value.rollingMean
            : rollingMean // ignore: cast_nullable_to_non_nullable
                  as double,
        contributionPercent: null == contributionPercent
            ? _value.contributionPercent
            : contributionPercent // ignore: cast_nullable_to_non_nullable
                  as double,
        history: null == history
            ? _value._history
            : history // ignore: cast_nullable_to_non_nullable
                  as List<double>,
        description: null == description
            ? _value.description
            : description // ignore: cast_nullable_to_non_nullable
                  as String,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$StressFactorImpl implements _StressFactor {
  const _$StressFactorImpl({
    required this.value,
    required this.trend,
    required this.rollingMean,
    required this.contributionPercent,
    required final List<double> history,
    required this.description,
  }) : _history = history;

  factory _$StressFactorImpl.fromJson(Map<String, dynamic> json) =>
      _$$StressFactorImplFromJson(json);

  @override
  final double value;
  @override
  final String trend;
  // 'up', 'down', 'stable'
  @override
  final double rollingMean;
  @override
  final double contributionPercent;
  final List<double> _history;
  @override
  List<double> get history {
    if (_history is EqualUnmodifiableListView) return _history;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_history);
  }

  // Micro-history for sparklines
  @override
  final String description;

  @override
  String toString() {
    return 'StressFactor(value: $value, trend: $trend, rollingMean: $rollingMean, contributionPercent: $contributionPercent, history: $history, description: $description)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StressFactorImpl &&
            (identical(other.value, value) || other.value == value) &&
            (identical(other.trend, trend) || other.trend == trend) &&
            (identical(other.rollingMean, rollingMean) ||
                other.rollingMean == rollingMean) &&
            (identical(other.contributionPercent, contributionPercent) ||
                other.contributionPercent == contributionPercent) &&
            const DeepCollectionEquality().equals(other._history, _history) &&
            (identical(other.description, description) ||
                other.description == description));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    value,
    trend,
    rollingMean,
    contributionPercent,
    const DeepCollectionEquality().hash(_history),
    description,
  );

  /// Create a copy of StressFactor
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$StressFactorImplCopyWith<_$StressFactorImpl> get copyWith =>
      __$$StressFactorImplCopyWithImpl<_$StressFactorImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$StressFactorImplToJson(this);
  }
}

abstract class _StressFactor implements StressFactor {
  const factory _StressFactor({
    required final double value,
    required final String trend,
    required final double rollingMean,
    required final double contributionPercent,
    required final List<double> history,
    required final String description,
  }) = _$StressFactorImpl;

  factory _StressFactor.fromJson(Map<String, dynamic> json) =
      _$StressFactorImpl.fromJson;

  @override
  double get value;
  @override
  String get trend; // 'up', 'down', 'stable'
  @override
  double get rollingMean;
  @override
  double get contributionPercent;
  @override
  List<double> get history; // Micro-history for sparklines
  @override
  String get description;

  /// Create a copy of StressFactor
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$StressFactorImplCopyWith<_$StressFactorImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
