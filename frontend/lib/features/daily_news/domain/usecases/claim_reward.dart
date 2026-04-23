import 'package:news_app_clean_architecture/core/resources/data_state.dart';
import 'package:news_app_clean_architecture/core/usecase/usecase.dart';

import '../repository/reward_repository.dart';


class ClaimRewardUseCase implements UseCase<DataState<Map<String, dynamic>>, ClaimRewardParams> {
  final RewardRepository _rewardRepository;

  ClaimRewardUseCase(this._rewardRepository);

  @override
  Future<DataState<Map<String, dynamic>>> call({ClaimRewardParams? params}) {
    return _rewardRepository.claimReward(params!.userId, params.articleId, params.readTime);
  }
}

class ClaimRewardParams {
  final String userId;
  final String articleId;
  final double readTime;

  ClaimRewardParams({required this.userId, required this.articleId, required this.readTime});
}
