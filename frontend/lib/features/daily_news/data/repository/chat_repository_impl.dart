import 'package:news_app_clean_architecture/features/daily_news/data/data_sources/remote/chat_service.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/repository/chat_repository.dart';

class ChatRepositoryImpl implements ChatRepository {
  final ChatService _chatService;

  ChatRepositoryImpl(this._chatService);

  @override
  Future<String> getChatResponse(List<Map<String, String>> messages) {
    return _chatService.getChatResponse(messages);
  }
}
