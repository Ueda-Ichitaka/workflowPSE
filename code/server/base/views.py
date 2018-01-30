import json

from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView, View

from base.models import InputOutput, WPSProvider, Process, Artefact, Edge, Task, Workflow, WPS


# TODO: tests, documentation
def as_json_response(list):
    """

    @param list:
    @type list:
    @return:
    @rtype:
    """
    return JsonResponse(list, safe=False)


class IndexView(TemplateView):
    template_name = "base/index.html"


# TODO: tests, documentation
class UserView(View):
    """

    """

    @staticmethod
    @require_GET
    def index(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        # TODO: Was not tested yet because of absence of user management in our project now
        return as_json_response(model_to_dict(request.user))


# TODO: tests, documentation
class WorkflowView(View):
    """

    """

    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        """

        @param args:
        @type args:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        return super(WorkflowView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        if 'workflow_id' in kwargs:
            workflow = Workflow.objects.get(pk=kwargs['workflow_id'])
            returned = model_to_dict(workflow)
            returned['edges'] = list(workflow.edge_set.all().values())
            tasks = list(workflow.task_set.all().values())

            for (i, task) in enumerate(tasks):
                tasks[i]['input_artefacts'] = list(Artefact.objects.filter(task=task['id']).filter(role=0).values())
                tasks[i]['output_artefacts'] = list(Artefact.objects.filter(task=task['id']).filter(role=1).values())
                tasks[i]['state'] = tasks[i]['status']

            returned['tasks'] = tasks
            return as_json_response(returned)
        else:
            returned = list(Workflow.objects.all().values())

            for (i, workflow) in enumerate(returned):
                tasks = list(Task.objects.filter(workflow=workflow['id']).values())

                for (j, task) in enumerate(tasks):
                    tasks[j]['input_artefacts'] = list(Artefact.objects.filter(task=task['id']).filter(role=0).values())
                    tasks[j]['output_artefacts'] = list(
                        Artefact.objects.filter(task=task['id']).filter(role=1).values())
                    tasks[j]['state'] = tasks[j]['status']

                returned[i]['tasks'] = tasks
                returned[i]['edges'] = list(Edge.objects.filter(workflow=workflow['id']).values())

            return as_json_response(returned)

    @staticmethod
    def post(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        new_data = json.loads(request.body)

        new_workflow = Workflow.objects.create(
            name=new_data['title'],
            percent_done=0,
            creator_id=1,  # TODO: request.user.id
            last_modifier_id=1  # TODO: request.user.id
        )

        temporary_to_new_task_ids = {}

        for new_task_data in new_data['tasks']:
            new_task = Task.objects.create(
                workflow_id=new_workflow.id,
                process_id=new_task_data['process_id'],
                x=new_task_data['x'],
                y=new_task_data['y'],
                status=new_task_data['state']
            )

            temporary_to_new_task_ids[new_task_data['id']] = new_task.id

            # TODO: kann man davon ausgehen, dass bei Erstellen auf jeden Fall keine Artefakte mitgeliefert werden?
            # TODO: ist es sinnvoll, Artefakte durch Workflow zu speichern? Vllt das in einen getrennten View packen?

        for new_edge_data in new_data['edges']:
            Edge.objects.create(
                workflow_id=new_workflow.id,
                from_task_id=temporary_to_new_task_ids[new_edge_data['a_id']],
                to_task_id=temporary_to_new_task_ids[new_edge_data['b_id']],
                input_id=new_edge_data['input_id'],
                output_id=new_edge_data['output_id']
            )

        return WorkflowView.get(request, workflow_id=new_workflow.id)

    @staticmethod
    def patch(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        new_data = json.loads(request.body)
        workflow = get_object_or_404(Workflow, pk=kwargs['workflow_id'])

        workflow.name = new_data['name']
        workflow.last_modifier_id = 1  # TODO: request.user.id

        workflow.save()

        temporary_to_new_task_ids = {}

        for task_data in new_data['tasks']:
            if task_data['id'] > 0:
                task = get_object_or_404(Task, pk=task_data['id'])

                task.workflow_id = workflow.id
                task.process_id = task_data['process_id']
                task.x = task_data['x']
                task.y = task_data['y']
                task.status = task_data['state']

                task.save()

                artefacts_data = task_data['input_artefacts'] + task_data['output_artefacts']

                for artefact_data in artefacts_data:
                    if ('id' in artefact_data) and (artefact_data['id'] > 0):
                        artefact = get_object_or_404(Artefact, pk=artefact_data['id'])

                        artefact.task_id = task.id
                        artefact.parameter_id = artefact_data['parameter_id']
                        artefact.role = (0 if artefact_data['role'] == 'input' else 1)
                        artefact.format = artefact_data['format']
                        artefact.data = artefact_data['data']

                        artefact.save()
                    else:
                        Artefact.objects.create(
                            task_id=task.id,
                            parameter_id=artefact_data['parameter_id'],
                            role=(0 if artefact_data['role'] == 'input' else 1),
                            format=artefact_data['format'],
                            data=artefact_data['data']
                        )
            else:
                task = Task.objects.create(
                    workflow_id=workflow.id,
                    process_id=task_data['process_id'],
                    x=task_data['x'],
                    y=task_data['y'],
                    status=task_data['state']
                )

            temporary_to_new_task_ids[task_data['id']] = task.id

        for edge_data in new_data['edges']:
            if edge_data['id'] > 0:
                edge = get_object_or_404(Edge, pk=edge_data['id'])

                edge.workflow = workflow
                edge.from_task_id = temporary_to_new_task_ids[edge_data['a_id']]
                edge.to_task_id = temporary_to_new_task_ids[edge_data['b_id']]
                edge.input_id = edge_data['input_id']
                edge.output_id = edge_data['output_id']

                edge.save()
            else:
                Edge.objects.create(
                    workflow_id=workflow.id,
                    from_task_id=temporary_to_new_task_ids[edge_data['a_id']],
                    to_task_id=temporary_to_new_task_ids[edge_data['b_id']],
                    input_id=edge_data['input_id'],
                    output_id=edge_data['output_id']
                )

        return WorkflowView.get(request, workflow_id=kwargs['workflow_id'])

    @staticmethod
    def delete(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        workflow = get_object_or_404(Workflow, pk=kwargs['workflow_id'])
        (deletedWorkflowCount, countOfDeletionsPerType) = workflow.delete()
        deleted = (deletedWorkflowCount > 0)

        return JsonResponse({'deleted': deleted})

    @staticmethod
    @require_GET
    def start(request, workflow_id):
        """

        @param request:
        @type request:
        @param workflow_id:
        @type workflow_id:
        @return:
        @rtype:
        """
        Task.objects.filter(workflow=workflow_id).update(status=1)

        return JsonResponse({})

    @staticmethod
    @require_GET
    def stop(request, workflow_id):
        """

        @param request:
        @type request:
        @param workflow_id:
        @type workflow_id:
        @return:
        @rtype:
        """
        Task.objects.filter(workflow=workflow_id).update(status=0)

        return JsonResponse({})


# TODO: tests, documentation
class ProcessView(View):
    """

    """

    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        """

        @param args:
        @type args:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        return super(ProcessView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        if 'process_id' in kwargs:
            process = Process.objects.get(pk=kwargs['process_id'])
            returned = model_to_dict(process)
            returned['inputs'] = list(process.inputoutput_set.all().filter(role=0).values())
            returned['outputs'] = list(process.inputoutput_set.all().filter(role=1).values())
            return as_json_response(returned)
        else:
            returned = list(Process.objects.all().values())

            for (i, process) in enumerate(returned):
                returned[i]['inputs'] = list(InputOutput.objects.filter(process=process['id']).filter(role=0).values())
                returned[i]['outputs'] = list(InputOutput.objects.filter(process=process['id']).filter(role=1).values())

            return as_json_response(returned)

    @staticmethod
    def post(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        new_data = json.loads(request.body)

        new_process = Process.objects.create(
            wps_id=new_data['wps_id'],
            identifier=new_data['identifier'],
            title=new_data['title'],
            abstract=new_data['abstract']
        )

        inputoutputs_data = new_data['inputs'] + new_data['outputs']

        for inputoutput_data in inputoutputs_data:
            InputOutput.objects.create(
                process_id=new_process.id,
                role=(0 if inputoutput_data['role'] == 'input' else 1),
                title=inputoutput_data['title'],
                abstract=inputoutput_data['abstract'],
                datatype=inputoutput_data['type'],
                min_occurs=inputoutput_data['min_occurs'],
                max_occurs=inputoutput_data['max_occurs']
            )

        return ProcessView.get(request, process_id=new_process.id)

    @staticmethod
    def patch(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        new_data = json.loads(request.body)
        process = get_object_or_404(Process, pk=kwargs['process_id'])

        process.wps_id = new_data['wps_id']
        process.identifier = new_data['identifier']
        process.title = new_data['title']
        process.abstract = new_data['abstract']

        process.save()

        inputoutputs_data = new_data['inputs'] + new_data['outputs']

        for inputoutput_data in inputoutputs_data:
            if inputoutput_data['id'] > 0:
                inputoutput = get_object_or_404(InputOutput, inputoutput_data['id'])

                inputoutput.process_id = process.id
                inputoutput.role = (0 if inputoutput_data['role'] == 'input' else 1)
                inputoutput.title = inputoutput_data['title']
                inputoutput.abstract = inputoutput_data['abstract']
                inputoutput.datatype = inputoutput_data['type']
                inputoutput.min_occurs = inputoutput_data['min_occurs']
                inputoutput.max_occurs = inputoutput_data['max_occurs']

                inputoutput.save()
            else:
                InputOutput.objects.create(
                    process_id=process.id,
                    role=(0 if inputoutput_data['role'] == 'input' else 1),
                    title=inputoutput_data['title'],
                    abstract=inputoutput_data['abstract'],
                    datatype=inputoutput_data['type'],
                    min_occurs=inputoutput_data['min_occurs'],
                    max_occurs=inputoutput_data['max_occurs']
                )

        return ProcessView.get(request, process_id=kwargs['process_id'])

    @staticmethod
    def delete(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        process = get_object_or_404(Process, pk=kwargs['process_id'])
        (deletedProcessCount, countOfDeletionsPerType) = process.delete()
        deleted = (deletedProcessCount > 0)

        return JsonResponse({'deleted': deleted})


# TODO: tests, documentation
class WPSView(View):
    """

    """

    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        """

        @param args:
        @type args:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        return super(WPSView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        if 'wps_id' in kwargs:
            wps = WPS.objects.get(pk=kwargs['wps_id'])
            returned = model_to_dict(wps)
            returned['provider'] = model_to_dict(wps.service_provider)
            return as_json_response(returned)
        else:
            returned = list(WPS.objects.all().values())

            for (i, wps) in enumerate(returned):
                returned[i]['provider'] = model_to_dict(WPSProvider.objects.get(pk=wps['service_provider_id']))

            return as_json_response(returned)

    @staticmethod
    def post(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        new_data = json.loads(request.body)

        new_wps_provider = WPSProvider.objects.create(
            provider_name=new_data['provider']['title'],
            provider_site=new_data['provider']['url']
        )

        new_wps = WPS.objects.create(
            service_provider_id=new_wps_provider.id,
            title=new_data['title'],
            abstract=new_data['abstract']
        )

        return WPSView.get(request, wps_id=new_wps.id)

    @staticmethod
    def patch(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        new_data = json.loads(request.body)
        wps = get_object_or_404(WPS, pk=kwargs['wps_id'])

        if new_data['provider']['id'] > 0:
            wps_provider = get_object_or_404(WPSProvider, pk=new_data['provider']['id'])

            wps_provider.provider_name = new_data['provider']['title']
            wps_provider.provider_site = new_data['provider']['url']

            wps_provider.save()

            wps_provider_id = new_data['provider']['id']
        else:
            new_wps_provider = WPSProvider.objects.create(
                provider_name=new_data['provider']['title'],
                provider_site=new_data['provider']['url']
            )

            wps_provider_id = new_wps_provider.id

        wps.service_provider_id = wps_provider_id
        wps.title = new_data['title']
        wps.abstract = new_data['abstract']

        wps.save()

        return WPSView.get(request, wps_id=kwargs['wps_id'])

    @staticmethod
    def delete(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        wps = get_object_or_404(Process, pk=kwargs['wps_id'])
        (deletedWPSCount, countOfDeletionsPerType) = wps.delete()
        deleted = (deletedWPSCount > 0)

        return JsonResponse({'deleted': deleted})

    @staticmethod
    @require_GET
    def refresh(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        return JsonResponse({})


# TODO: tests, documentation
class WorkflowsView(TemplateView):
    """

    """
    template_name = "base/workflows.html"


# TODO: tests, documentation
class EditorView(TemplateView):
    """

    """
    template_name = "base/editor.html"


# TODO: tests, documentation
class SettingsView(TemplateView):
    """

    """
    template_name = "base/settings.html"
