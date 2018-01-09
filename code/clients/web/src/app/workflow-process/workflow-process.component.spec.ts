import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { WorkflowProcessComponent } from './workflow-process.component';

describe('WorkflowProcessComponent', () => {
  let component: WorkflowProcessComponent;
  let fixture: ComponentFixture<WorkflowProcessComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ WorkflowProcessComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(WorkflowProcessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
