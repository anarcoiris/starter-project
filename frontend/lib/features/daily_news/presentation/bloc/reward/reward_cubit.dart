import 'package:news_app_clean_architecture/core/resources/data_state.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/usecases/claim_reward.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/usecases/get_balance.dart';


import 'reward_state.dart';


class RewardCubit extends Cubit<RewardState> {
  final ClaimRewardUseCase _claimRewardUseCase;
  final GetBalanceUseCase _getBalanceUseCase;

  RewardCubit(this._claimRewardUseCase, this._getBalanceUseCase) : super(RewardInitial());

  Future<void> claimReward(String userId, String articleUrl, double readTime) async {
    if (articleUrl.isEmpty) return;

    emit(RewardClaiming());

    final dataState = await _claimRewardUseCase(
      params: ClaimRewardParams(userId: userId, articleId: articleUrl, readTime: readTime)
    );

    if (dataState is DataSuccess && dataState.data != null) {
      final result = dataState.data!;
      if (result['status'] == 'success') {
        final amount = (result['reward'] as num).toDouble();
        emit(RewardClaimSuccess(amount, result['message'] ?? 'Recompensa obtenida'));
      } else {
        emit(RewardClaimError(result['message'] ?? 'Fallo al reclamar recompensa'));
      }
    }

    if (dataState is DataFailed) {
      String errorMessage = dataState.error?.message ?? 'Error de conexión';
      emit(RewardClaimError(errorMessage));
    }
  }

  Future<double> getBalance(String userId) async {
    final dataState = await _getBalanceUseCase(params: userId);
    
    if (dataState is DataSuccess && dataState.data != null) {
      return dataState.data!;
    }
    return 0.0;
  }
}

