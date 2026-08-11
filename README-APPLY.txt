EULOGIA WIKI ITEM-PAGE UPDATE

1. Extract this ZIP into C:\Eulogia\Eulogia-Wiki and allow overwrite.
2. Open PowerShell in C:\Eulogia\Eulogia-Wiki
3. Run:
   .\apply-update.ps1
4. Preview if desired:
   .\.venv\Scripts\python.exe -m mkdocs serve
5. Publish:
   git add .
   git commit -m "Reorganize enchantments by compatible item"
   git push

The generator uses the existing data\enchantments.csv in your repository.
The reference\enchantments-validated-160.csv copy is only a backup/reference and is not used by the generator.
