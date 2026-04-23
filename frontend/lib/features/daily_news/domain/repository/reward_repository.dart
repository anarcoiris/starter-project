import '../../../../core/resources/data_state.dart';

abstract class RewardRepository {
  Future<DataState<double>> getBalance(String userId);
  Future<DataState<Map<String, dynamic>>> claimReward(String userId, String articleId, double readTime);
}
