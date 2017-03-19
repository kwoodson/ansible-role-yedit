ANSIBLE_MODULE_FILE=library/yedit.py


all: ansible test


test: test-style test-unit test-ansible

test-style:
	pylint yedit

test-unit:
	PYTHONPATH=. python test/units.py

test-ansible:
	ANSIBLE_STDOUT_CALLBACK=actionable ansible-playbook test/ansible/*.yml

ansible:
	stickytape yedit/__main__.py > $(ANSIBLE_MODULE_FILE)

clean:
	rm -f $(ANSIBLE_MODULE_FILE)
