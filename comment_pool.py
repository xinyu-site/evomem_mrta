from comment import Comment


class CommentPool(object):

    def __init__(self, all_agents, visible_matrix):
        """A global data structure store current comments.

        Args:
            agents: list of Baseagent
            visible_matrix: two-dimension numpy array
        """
        self.comments = []
        self.all_agents = all_agents
        self.agent_name_to_id = { agent.name: i for i, agent in enumerate(all_agents) }
        self.visible_matrix = visible_matrix

    def add_comment(self, comment: Comment):
        self.comments.append(comment)

    def get_comments(self, agent_name):    #获取智能体评论
        """Get comments by agent's name
        
        Args
            agent_name: str
        """
        id_ = self.agent_name_to_id[agent_name]
        visible_indices = self.visible_matrix[id_]

        comment_list = []
        for comment in self.comments:
            target_id = self.agent_name_to_id[comment.agent.name]
            if visible_indices[target_id] == 1:
                comment_list.append(comment)
        return comment_list
    
    def get_current_comment_text(self):
        comments_text = ''
        if len(self.comments) == 0:
            comments_text = 'There is no comment available, please ignore this section.\n'
        else:
            for comment in self.comments:
                comments_text += comment.agent.name + ': ```' + comment.comment_text + '```\n'
        return comments_text
    
    def __len__(self):
        return len(self.comments)
