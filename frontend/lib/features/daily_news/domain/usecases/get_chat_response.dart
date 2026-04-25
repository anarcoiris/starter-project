import 'package:news_app_clean_architecture/core/usecase/usecase.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/repository/chat_repository.dart';

class GetChatResponseUseCase implements UseCase<String, List<Map<String, String>>> {
  final ChatRepository _chatRepository;

  GetChatResponseUseCase(this._chatRepository);

  @override
  Future<String> call({List<Map<String, String>>? params}) {
    return _chatRepository.getChatResponse(params!);
  }
}
