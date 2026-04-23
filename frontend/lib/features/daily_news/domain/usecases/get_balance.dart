import 'package:news_app_clean_architecture/core/resources/data_state.dart';
import 'package:news_app_clean_architecture/core/usecase/usecase.dart';

import '../repository/reward_repository.dart';


class GetBalanceUseCase implements UseCase<DataState<double>, String> {
  final RewardRepository _rewardRepository;

  GetBalanceUseCase(this._rewardRepository);

  @override
  Future<DataState<double>> call({String? params}) {
    return _rewardRepository.getBalance(params!);
  }
}
