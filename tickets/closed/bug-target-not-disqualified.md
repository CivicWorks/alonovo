# Bug: Target shows B+ overall grade despite ICE Collaborator F

## Where
Company detail page for Target (TGT), and company card on main page

## What
Target has `ice_collaborator` value with grade F and badge "Refused to protect employees". According to the grading rules, companies with F on a disqualifying value (ICE Detention, ICE Collaborator) should have F as their overall grade. But Target's `scores[0].grade` is "B+" — it's not being disqualified.

## Expected
Target's overall grade should be F (disqualified by ICE Collaborator).

## Steps to Reproduce
1. Go to https://demos.linkedtrust.us/alonovo/
2. Search for "Target"
3. See overall grade is B+ instead of F

## API Evidence
```
GET /api/companies/ → Target entry:
  scores[0].grade = "B+"
  value_snapshots includes ice_collaborator with grade "F"
```

## Notes
Other disqualified companies (GEO Group, CoreCivic, Palantir, Avelo Airlines) correctly have no overall score in `scores[]`, so they default correctly. Target is the only one with a pre-existing score that wasn't updated after the ICE Collaborator data was added.
