import langchain, langchain_community, langchain_experimental, pkg_resources, sys; \
print('langchain', langchain.__version__); \
print('langchain_community', langchain_community.__version__); \
print('langchain_experimental', langchain_experimental.__version__)




from langchain_community.utilities import SQLDatabase        # ✅ present in 0.2.19
from langchain_experimental.sql    import SQLDatabaseChain   # ✅ present in 0.0.65

print("Both imports succeeded!")


