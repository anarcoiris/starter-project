abstract class ChatRepository {
  Future<String> getChatResponse(List<Map<String, String>> messages);
}
