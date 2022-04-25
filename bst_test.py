from binarytree import BinaryTree

tree = BinaryTree()

tree.insert((1,0), 'one')
tree.insert((2,0), 'two')
tree.insert((8,0), 'eight')
tree.insert((0,0), 'zero')
tree.insert((1,1), 'one v2')

print(tree.get_val_from_closest_key((1,2)))
print(tree.get_inorder())


