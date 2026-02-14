// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'risk_snapshot.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

RiskSnapshot _$RiskSnapshotFromJson(Map<String, dynamic> json) {
  return _RiskSnapshot.fromJson(json);
}

/// @nodoc
mixin _$RiskSnapshot {
  DateTime get timestamp => throw _privateConstructorUsedError;
  int get riskScore => throw _privateConstructorUsedError;
  double get confidence => throw _privateConstructorUsedError;
  String? get event => throw _privateConstructorUsedError;

  /// Serializes this RiskSnapshot to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of RiskSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $RiskSnapshotCopyWith<RiskSnapshot> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $RiskSnapshotCopyWith<$Res> {
  factory $RiskSnapshotCopyWith(
    RiskSnapshot value,
    $Res Function(RiskSnapshot) then,
  ) = _$RiskSnapshotCopyWithImpl<$Res, RiskSnapshot>;
  @useResult
  $Res call({
    DateTime timestamp,
    int riskScore,
    double confidence,
    String? event,
  });
}

/// @nodoc
class _$RiskSnapshotCopyWithImpl<$Res, $Val extends RiskSnapshot>
    implements $RiskSnapshotCopyWith<$Res> {
  _$RiskSnapshotCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of RiskSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? timestamp = null,
    Object? riskScore = null,
    Object? confidence = null,
    Object? event = freezed,
  }) {
    return _then(
      _value.copyWith(
            timestamp: null == timestamp
                ? _value.timestamp
                : timestamp // ignore: cast_nullable_to_non_nullable
                      as DateTime,
            riskScore: null == riskScore
                ? _value.riskScore
                : riskScore // ignore: cast_nullable_to_non_nullable
                      as int,
            confidence: null == confidence
                ? _value.confidence
                : confidence // ignore: cast_nullable_to_non_nullable
                      as double,
            event: freezed == event
                ? _value.event
                : event // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$RiskSnapshotImplCopyWith<$Res>
    implements $RiskSnapshotCopyWith<$Res> {
  factory _$$RiskSnapshotImplCopyWith(
    _$RiskSnapshotImpl value,
    $Res Function(_$RiskSnapshotImpl) then,
  ) = __$$RiskSnapshotImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    DateTime timestamp,
    int riskScore,
    double confidence,
    String? event,
  });
}

/// @nodoc
class __$$RiskSnapshotImplCopyWithImpl<$Res>
    extends _$RiskSnapshotCopyWithImpl<$Res, _$RiskSnapshotImpl>
    implements _$$RiskSnapshotImplCopyWith<$Res> {
  __$$RiskSnapshotImplCopyWithImpl(
    _$RiskSnapshotImpl _value,
    $Res Function(_$RiskSnapshotImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of RiskSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? timestamp = null,
    Object? riskScore = null,
    Object? confidence = null,
    Object? event = freezed,
  }) {
    return _then(
      _$RiskSnapshotImpl(
        timestamp: null == timestamp
            ? _value.timestamp
            : timestamp // ignore: cast_nullable_to_non_nullable
                  as DateTime,
        riskScore: null == riskScore
            ? _value.riskScore
            : riskScore // ignore: cast_nullable_to_non_nullable
                  as int,
        confidence: null == confidence
            ? _value.confidence
            : confidence // ignore: cast_nullable_to_non_nullable
                  as double,
        event: freezed == event
            ? _value.event
            : event // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$RiskSnapshotImpl implements _RiskSnapshot {
  const _$RiskSnapshotImpl({
    required this.timestamp,
    required this.riskScore,
    required this.confidence,
    this.event,
  });

  factory _$RiskSnapshotImpl.fromJson(Map<String, dynamic> json) =>
      _$$RiskSnapshotImplFromJson(json);

  @override
  final DateTime timestamp;
  @override
  final int riskScore;
  @override
  final double confidence;
  @override
  final String? event;

  @override
  String toString() {
    return 'RiskSnapshot(timestamp: $timestamp, riskScore: $riskScore, confidence: $confidence, event: $event)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$RiskSnapshotImpl &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.riskScore, riskScore) ||
                other.riskScore == riskScore) &&
            (identical(other.confidence, confidence) ||
                other.confidence == confidence) &&
            (identical(other.event, event) || other.event == event));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, timestamp, riskScore, confidence, event);

  /// Create a copy of RiskSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$RiskSnapshotImplCopyWith<_$RiskSnapshotImpl> get copyWith =>
      __$$RiskSnapshotImplCopyWithImpl<_$RiskSnapshotImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$RiskSnapshotImplToJson(this);
  }
}

abstract class _RiskSnapshot implements RiskSnapshot {
  const factory _RiskSnapshot({
    required final DateTime timestamp,
    required final int riskScore,
    required final double confidence,
    final String? event,
  }) = _$RiskSnapshotImpl;

  factory _RiskSnapshot.fromJson(Map<String, dynamic> json) =
      _$RiskSnapshotImpl.fromJson;

  @override
  DateTime get timestamp;
  @override
  int get riskScore;
  @override
  double get confidence;
  @override
  String? get event;

  /// Create a copy of RiskSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$RiskSnapshotImplCopyWith<_$RiskSnapshotImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
