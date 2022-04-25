from node import Node

CLOSEST = 9999

class BinaryTree:
    '''
    Stor static GTFS file lists as a Binary tree
    '''
    def __init__(self):
        self.root = None

    def insert(self, key, val):
        new_node = Node(key[0], {key[1]: val})
        
        if self.root is None:
            self.root = new_node

        cur = self.root
        while cur is not None:
            if new_node.key > cur.key:
                if cur.right is None:
                    cur.right = new_node
                    return
                cur = cur.right
            elif new_node.key < cur.key:
                if cur.left is None:
                    cur.left = new_node
                    return
                cur = cur.left
            else:
                cur.val[key[1]] = val
                return

    # do not use
    def search(self, n):
        if self.root is None:
            return None

        cur = self.root
        while cur is not None:
            if n[0] > cur.key:
                cur = cur.right
                continue
            elif n[0] < cur.key:
                cur = cur.left
                continue
            else:
                return cur.val[n[1]]

        return None

    def get_val_from_closest_key(self, n, closest=[CLOSEST,None]):
        result_dict = self.search_closest_recursion(self.root, n[0], closest).val
        closest_key = min(result_dict, key=lambda x:abs(x-n[1]))
        return result_dict[closest_key]

    def get_closest_key(self, n, closest=[CLOSEST,None]):
        result_key = self.search_closest_recursion(self.root, n[0], closest).key
        return result_key

    def search_closest_recursion(self, root, n, closest=[CLOSEST,None]):
        if root is None:
            return closest[1]

        if abs(root.key - n) < abs(closest[0] - n):
            closest[0] = root.key
            closest[1] = root
        if n < root.key:
            return self.search_closest_recursion(root.left, n, closest)
        else:
            return self.search_closest_recursion(root.right, n, closest)

    def get_inorder(self):
        tree_list = []
        self.get_inorder_recursion(self.root, tree_list)
        return tree_list

    def get_inorder_recursion(self, root, tree_list):
        if root:
            self.get_inorder_recursion(root.left, tree_list)
            tree_list.extend(list(root.val.values()))
            self.get_inorder_recursion(root.right, tree_list)

    def inorder(self):
        self.inorder_recursion(self.root)

    def inorder_recursion(self, root):
        if root:
            self.inorder_recursion(root.left)
            print(root.key, end=' ')
            self.inorder_recursion(root.right)
