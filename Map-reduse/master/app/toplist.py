class TopList:
    def __init__(self, top_count: int, key: None, buffer_limit: int = None):
        self.__top_count = top_count
        self.__key = key
        self.__buffer_limit = buffer_limit if buffer_limit else top_count * 2
        self.__buffer = []
    
    def get_top(self) -> None:
        return sorted(
            self.__buffer,
            key = self.__key,
            reverse=True
        )[:self.__top_count]
        
    def add(self, item) -> None:
        self.__buffer.append(item)
        if len(self.__buffer) > self.__buffer_limit:
            self.__buffer = self.get_top()
    
    def add_list(self, items: list) -> None:
        for item in items:
            self.add(item)