// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'chain_finality_data.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

ChainFinalityData _$ChainFinalityDataFromJson(Map<String, dynamic> json) {
  return _ChainFinalityData.fromJson(json);
}

/// @nodoc
mixin _$ChainFinalityData {
  String get chain => throw _privateConstructorUsedError;
  int get confirmations => throw _privateConstructorUsedError;
  String get tier =>
      throw _privateConstructorUsedError; // e.g., 'Tier 1', 'Tier 2'
  bool get finalized => throw _privateConstructorUsedError;
  DateTime get lastReorg => throw _privateConstructorUsedError;
  double get confidence => throw _privateConstructorUsedError;

  /// Serializes this ChainFinalityData to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ChainFinalityData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ChainFinalityDataCopyWith<ChainFinalityData> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChainFinalityDataCopyWith<$Res> {
  factory $ChainFinalityDataCopyWith(
    ChainFinalityData value,
    $Res Function(ChainFinalityData) then,
  ) = _$ChainFinalityDataCopyWithImpl<$Res, ChainFinalityData>;
  @useResult
  $Res call({
    String chain,
    int confirmations,
    String tier,
    bool finalized,
    DateTime lastReorg,
    double confidence,
  });
}

/// @nodoc
class _$ChainFinalityDataCopyWithImpl<$Res, $Val extends ChainFinalityData>
    implements $ChainFinalityDataCopyWith<$Res> {
  _$ChainFinalityDataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ChainFinalityData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? chain = null,
    Object? confirmations = null,
    Object? tier = null,
    Object? finalized = null,
    Object? lastReorg = null,
    Object? confidence = null,
  }) {
    return _then(
      _value.copyWith(
            chain: null == chain
                ? _value.chain
                : chain // ignore: cast_nullable_to_non_nullable
                      as String,
            confirmations: null == confirmations
                ? _value.confirmations
                : confirmations // ignore: cast_nullable_to_non_nullable
                      as int,
            tier: null == tier
                ? _value.tier
                : tier // ignore: cast_nullable_to_non_nullable
                      as String,
            finalized: null == finalized
                ? _value.finalized
                : finalized // ignore: cast_nullable_to_non_nullable
                      as bool,
            lastReorg: null == lastReorg
                ? _value.lastReorg
                : lastReorg // ignore: cast_nullable_to_non_nullable
                      as DateTime,
            confidence: null == confidence
                ? _value.confidence
                : confidence // ignore: cast_nullable_to_non_nullable
                      as double,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$ChainFinalityDataImplCopyWith<$Res>
    implements $ChainFinalityDataCopyWith<$Res> {
  factory _$$ChainFinalityDataImplCopyWith(
    _$ChainFinalityDataImpl value,
    $Res Function(_$ChainFinalityDataImpl) then,
  ) = __$$ChainFinalityDataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String chain,
    int confirmations,
    String tier,
    bool finalized,
    DateTime lastReorg,
    double confidence,
  });
}

/// @nodoc
class __$$ChainFinalityDataImplCopyWithImpl<$Res>
    extends _$ChainFinalityDataCopyWithImpl<$Res, _$ChainFinalityDataImpl>
    implements _$$ChainFinalityDataImplCopyWith<$Res> {
  __$$ChainFinalityDataImplCopyWithImpl(
    _$ChainFinalityDataImpl _value,
    $Res Function(_$ChainFinalityDataImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of ChainFinalityData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? chain = null,
    Object? confirmations = null,
    Object? tier = null,
    Object? finalized = null,
    Object? lastReorg = null,
    Object? confidence = null,
  }) {
    return _then(
      _$ChainFinalityDataImpl(
        chain: null == chain
            ? _value.chain
            : chain // ignore: cast_nullable_to_non_nullable
                  as String,
        confirmations: null == confirmations
            ? _value.confirmations
            : confirmations // ignore: cast_nullable_to_non_nullable
                  as int,
        tier: null == tier
            ? _value.tier
            : tier // ignore: cast_nullable_to_non_nullable
                  as String,
        finalized: null == finalized
            ? _value.finalized
            : finalized // ignore: cast_nullable_to_non_nullable
                  as bool,
        lastReorg: null == lastReorg
            ? _value.lastReorg
            : lastReorg // ignore: cast_nullable_to_non_nullable
                  as DateTime,
        confidence: null == confidence
            ? _value.confidence
            : confidence // ignore: cast_nullable_to_non_nullable
                  as double,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$ChainFinalityDataImpl implements _ChainFinalityData {
  const _$ChainFinalityDataImpl({
    required this.chain,
    required this.confirmations,
    required this.tier,
    required this.finalized,
    required this.lastReorg,
    required this.confidence,
  });

  factory _$ChainFinalityDataImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChainFinalityDataImplFromJson(json);

  @override
  final String chain;
  @override
  final int confirmations;
  @override
  final String tier;
  // e.g., 'Tier 1', 'Tier 2'
  @override
  final bool finalized;
  @override
  final DateTime lastReorg;
  @override
  final double confidence;

  @override
  String toString() {
    return 'ChainFinalityData(chain: $chain, confirmations: $confirmations, tier: $tier, finalized: $finalized, lastReorg: $lastReorg, confidence: $confidence)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChainFinalityDataImpl &&
            (identical(other.chain, chain) || other.chain == chain) &&
            (identical(other.confirmations, confirmations) ||
                other.confirmations == confirmations) &&
            (identical(other.tier, tier) || other.tier == tier) &&
            (identical(other.finalized, finalized) ||
                other.finalized == finalized) &&
            (identical(other.lastReorg, lastReorg) ||
                other.lastReorg == lastReorg) &&
            (identical(other.confidence, confidence) ||
                other.confidence == confidence));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    chain,
    confirmations,
    tier,
    finalized,
    lastReorg,
    confidence,
  );

  /// Create a copy of ChainFinalityData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ChainFinalityDataImplCopyWith<_$ChainFinalityDataImpl> get copyWith =>
      __$$ChainFinalityDataImplCopyWithImpl<_$ChainFinalityDataImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$ChainFinalityDataImplToJson(this);
  }
}

abstract class _ChainFinalityData implements ChainFinalityData {
  const factory _ChainFinalityData({
    required final String chain,
    required final int confirmations,
    required final String tier,
    required final bool finalized,
    required final DateTime lastReorg,
    required final double confidence,
  }) = _$ChainFinalityDataImpl;

  factory _ChainFinalityData.fromJson(Map<String, dynamic> json) =
      _$ChainFinalityDataImpl.fromJson;

  @override
  String get chain;
  @override
  int get confirmations;
  @override
  String get tier; // e.g., 'Tier 1', 'Tier 2'
  @override
  bool get finalized;
  @override
  DateTime get lastReorg;
  @override
  double get confidence;

  /// Create a copy of ChainFinalityData
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ChainFinalityDataImplCopyWith<_$ChainFinalityDataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
