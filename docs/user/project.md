# Project Module
The project module provides the building blocks for managing projects within the NINA DMS. A project is a central entity that provides permissions over a certain dataset. Projects are organizational units and are used to group together both users, datasets and services.

**NOTES**: the project module is heavily dependent on the work organization at NINA, and might need to be adapted for other organizations.


## DMP
Each project can have an associated Data Management Plan (DMP). The DMP is a structured document that describes how data will be managed throughout the lifecycle of the project.

The NINA DMP provides helpful tips to fill each field, with relevant options for NINA projects.

If your project requires to use a different DMP template it's still possible to upload a file (PDF or Word).

It's possible to export the DMP as PDF, Word or LaTeX document.

It's possible to have draft versions of a DMP, just do not connect the DMP to the project until it's ready.

**NOTE**: only the project leader can assign or change the DMP associated with a project.

## NINA Specific
A NINA project is associated with a fund (financing source) and has a project manager (a user responsible for the project).

Projects can be hierarchical, with parent and child projects. This heierarchy is NOT implemented in the system, but can be inferred by looking at the project codes.

Projects are syncronized by an external system that runs periodically and updates the project list using the data from the ERP system.
