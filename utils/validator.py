def validate_poem_data(poem):
    """验证诗歌数据格式"""
    required_fields = ['title', 'author', 'dynasty', 'content', 'translation', 'explanation']
    
    for field in required_fields:
        if field not in poem:
            return False, f"缺少必要字段: {field}"
    
    if not isinstance(poem['content'], str) or len(poem['content']) < 10:
        return False, "诗歌内容格式错误"
    
    return True, "数据格式正确"

def get_poem_stats(poems):
    """获取诗歌统计信息"""
    stats = {
        'total': len(poems),
        'authors': len(set(poem['author'] for poem in poems)),
        'avg_length': sum(len(poem['content']) for poem in poems) / len(poems) if poems else 0
    }
    return stats