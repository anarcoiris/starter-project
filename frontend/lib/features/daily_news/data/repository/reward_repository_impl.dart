import 'dart:io';
import 'package:dio/dio.dart';
import '../../../../core/resources/data_state.dart';
import '../../domain/repository/reward_repository.dart';
import '../data_sources/remote/reward_api_service.dart';

class RewardRepositoryImpl implements RewardRepository {
  final RewardApiService _rewardApiService;

  RewardRepositoryImpl(this._rewardApiService);

  @override
  Future<DataState<Map<String, dynamic>>> claimReward(String userId, String articleId, double readTime) async {
    try {
      final result = await _rewardApiService.claimReward(userId, articleId, readTime);
      return DataSuccess(result);
    } on DioException catch (e) {
      return DataFailed(e);
    } catch (e) {
      return DataFailed(
        DioException(
          requestOptions: RequestOptions(path: ''),
          error: e.toString(),
          type: DioExceptionType.unknown,
        ),
      );
    }
  }

  @override
  Future<DataState<double>> getBalance(String userId) async {
    try {
      final result = await _rewardApiService.getBalance(userId);
      final balance = (result['balance'] as num).toDouble();
      return DataSuccess(balance);
    } on DioException catch (e) {
      return DataFailed(e);
    } catch (e) {
       return DataFailed(
        DioException(
          requestOptions: RequestOptions(path: ''),
          error: e.toString(),
          type: DioExceptionType.unknown,
        ),
      );
    }
  }
}
